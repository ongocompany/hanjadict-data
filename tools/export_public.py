#!/usr/bin/env python3
"""앱 자료 묶음 dict.db 에서 공개용 사전 데이터(CC BY-SA 4.0)를 내보낸다.

진우 결정(2026-10-22): 국립국어원 두 사전·CC-CEDICT 에서 온 표와 Unihan 에서 온 글자 정보를 공개하고,
한국어문회 배정한자 자료와 앱 내부용 표는 뺀다.

  넣는다  ko_words ko_senses ko_zh_equivs ko_synonyms zh_words zh_senses ko_zh_links
          ko_char_words zh_char_words notes glyphs char_variants(source 가 unihan·cedict 인 행)
          + 새로 만든 공개용 meta
  뺀다    characters 표 전체, char_variants 의 source='eomunhoe' 행,
          search_keys, zh_audio, 원본 meta (빌드 경로 따위),
          notes 의 녹음 경로(audio_word 열, examples 안의 audio 키 — 녹음 파일은 이번에 공개하지 않는다)

내는 것 (--out 디렉터리):
  hanjadict-data.sqlite      공개 SQLite (표 12개 + meta, 색인 포함)
  tsv/<표>.tsv               표마다 UTF-8 TSV (머리줄 있음). 같은 내용을 SQLite 와 둘 다 낸다.
  [--repo]  공개 저장소에 schema.sql · SCHEMA.md · samples/ · README 건수 블록 · tools/export_public.py
  [--dist]  GitHub Releases 에 올릴 압축본 + SHA256SUMS

TSV 형식: 탭으로 나누고 줄마다 한 행. 칸 안의 탭·줄바꿈·역슬래시는 \\t \\n \\r \\\\ 로 쓴다.
NULL 은 빈 칸이다 (NULL 이 될 수 있는 열에는 빈 문자열이 없다는 것을 검사한다).
JSONL 대신 TSV 를 고른 까닭: 이 자료는 평평한 표 12개이고 884,174행 · 427,601행짜리 두 글자-낱말
연결 표처럼 열이 둘뿐인 큰 표가 많아 JSONL 은 행마다 열 이름을 되풀이해 훨씬 커진다. TSV 는 엑셀·pandas·DuckDB·
sqlite3 .import 가 바로 읽고 git diff 도 줄 단위로 보인다. 여러 줄 구조는 notes.examples 한 칸(JSON 문자열)뿐이다.

사용:
  python3 pipeline/v2/export_public.py --out /경로/build \\
      [--db resources/dict.db] [--repo /경로/hanjadict-data] [--dist /경로/hanjadict-data/dist]

원본 dict.db 는 mode=ro 로만 열고 하나의 읽기 트랜잭션 안에서 복사한다. 마지막에 공개본 검사를 돌리고
하나라도 어긋나면 종료 코드 1 로 끝난다.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tarfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DEFAULT_DB = os.path.join(REPO, "resources", "dict.db")

DATASET_NAME = "hanjadict-data"
LICENSE_ID = "CC-BY-SA-4.0"
PUBLIC_SCHEMA_VERSION = "1"
SAMPLE_ROWS = 30

# 공개본에 있어서는 안 되는 문자열 (경로는 이 파일 자체가 걸리지 않게 이어 붙여 만든다)
LOCAL_PATH = "/" + "Users" + "/"
FORBIDDEN_TEXT = (LOCAL_PATH, "eomunhoe", "/home/", "resources/dict")
FORBIDDEN_TABLES = ("characters", "search_keys", "zh_audio")
FORBIDDEN_COLUMNS = ("level_code", "level_label", "long_sound", "audio_word", "path")

NOTES_AUDIO_KEY = "audio"

# ---------------------------------------------------------------------------
# 표 정의. 열: (이름, 형, 제약, 설명). 형·제약은 앱 dict.db 와 같다 (notes 의 audio_word 만 뺐다).
# 이 정의가 DDL · SCHEMA.md · TSV 머리줄의 단일 원본이다.
# ---------------------------------------------------------------------------

C = lambda name, typ, cons, doc: (name, typ, cons, doc)  # noqa: E731

TABLES = [
    dict(
        name="ko_words",
        origin="표준국어대사전 · 한국어기초사전",
        title="한국어 낱말",
        desc="표준국어대사전의 한자어·혼종어(원어 한자가 있는 낱말 전부)와, 한자·중국어로 이어지는 고유어. "
             "한국어기초사전의 등급을 붙였다.",
        cols=[
            C("id", "INTEGER", "PRIMARY KEY", "낱말 번호. 다른 표가 이 번호로 가리킨다."),
            C("headword", "TEXT", "NOT NULL", "표제어 (예: 신문). 동음이의 번호는 homonym_no 로 떼어 두었다."),
            C("homonym_no", "INTEGER", "", "동음이의어 번호. 없으면 빈 칸."),
            C("hanja", "TEXT", "NOT NULL", "원어 한자 (예: 新聞). 고유어는 빈 문자열."),
            C("word_type", "TEXT", "", "어종: 고유어 · 한자어 · 혼종어 (표준국어대사전)."),
            C("pos", "TEXT", "", "품사 (표준국어대사전). 없으면 '품사 없음'."),
            C("pronunciation", "TEXT", "", "발음 (표준국어대사전). ː 는 긴소리."),
            C("is_affix", "INTEGER", "NOT NULL DEFAULT 0", "접사·어근 따위 붙는 말이면 1."),
            C("level", "INTEGER", "", "한국어기초사전 등급: 1 초급, 2 중급, 3 고급, 4 등급 없이 수록. 미수록은 빈 칸."),
            C("rank", "INTEGER", "NOT NULL", "앱이 목록을 줄 세우는 값 (작을수록 먼저). 등급·중국어 연결·글자 수·동음이의 번호로 만든다."),
        ],
    ),
    dict(
        name="ko_senses",
        origin="표준국어대사전",
        title="한국어 뜻풀이",
        desc="ko_words 의 뜻풀이. 낱말 하나에 뜻이 여럿이면 여러 행.",
        cols=[
            C("word_id", "INTEGER", "NOT NULL", "ko_words.id"),
            C("sense_no", "INTEGER", "", "뜻 번호."),
            C("definition", "TEXT", "NOT NULL", "뜻풀이 원문 (표준국어대사전)."),
            C("category", "TEXT", "", "전문 분야·갈래 표지 (예: 역사). 없으면 빈 칸."),
        ],
    ),
    dict(
        name="ko_zh_equivs",
        origin="한국어기초사전",
        title="한국어 뜻별 중국어 대응어",
        desc="한국어기초사전이 뜻풀이마다 달아 둔 중국어 대응어. 쉼표 · ， · 、 로 나눈 후보 하나가 한 행. "
             "ko_words 와 표제+원어(고유어는 표제+품사)로 맞춘 것만 들었다.",
        cols=[
            C("word_id", "INTEGER", "NOT NULL", "ko_words.id"),
            C("ord", "INTEGER", "NOT NULL", "보여 줄 순서 (0부터)."),
            C("ko_definition", "TEXT", "NOT NULL", "그 대응어가 달린 한국어기초사전 뜻풀이."),
            C("zh", "TEXT", "NOT NULL", "중국어 대응어 한 후보."),
            C("zh_word_id", "INTEGER", "", "zh_words 에 같은 간체 표제가 있으면 그 id (여럿이면 rank 가 가장 작은 것)."),
        ],
    ),
    dict(
        name="ko_synonyms",
        origin="표준국어대사전",
        title="고유어의 같은 뜻 한자어",
        desc="고유어 낱말 뜻에 달린 동의어·비슷한말 중 한자어인 것.",
        cols=[
            C("word_id", "INTEGER", "NOT NULL", "고유어 ko_words.id"),
            C("syn_id", "INTEGER", "NOT NULL", "한자가 있는 ko_words.id"),
            C("kind", "TEXT", "NOT NULL", "동의어 | 비슷한말"),
            C("ord", "INTEGER", "NOT NULL", "보여 줄 순서."),
        ],
        pk=("word_id", "syn_id"),
    ),
    dict(
        name="zh_words",
        origin="CC-CEDICT",
        title="중국어 낱말",
        desc="CC-CEDICT 표제 전체. HSK 3.0 등급 값을 붙였다.",
        cols=[
            C("id", "INTEGER", "PRIMARY KEY", "낱말 번호."),
            C("simplified", "TEXT", "NOT NULL", "간체 표제."),
            C("traditional", "TEXT", "NOT NULL", "번체 표제."),
            C("pinyin", "TEXT", "NOT NULL", "병음 (성조 부호, 음절 사이 공백)."),
            C("pinyin_num", "TEXT", "NOT NULL", "CC-CEDICT 원문 숫자 성조 병음 (xue2 xi2)."),
            C("hsk", "INTEGER", "", "HSK 3.0 등급 1..6, 7 은 7-9급. 등급 밖은 빈 칸."),
            C("rank", "INTEGER", "NOT NULL", "앱이 목록을 줄 세우는 값 (작을수록 먼저)."),
        ],
    ),
    dict(
        name="zh_senses",
        origin="CC-CEDICT · 한국어 풀이는 AI 번역 2차 저작물",
        title="중국어 풀이",
        desc="zh_words 의 풀이. en 은 CC-CEDICT 원문, ko 는 그 영어 풀이를 AI 로 한국어로 옮긴 2차 저작물이다 "
             "(사람이 검수하기 전이라 틀린 곳이 있을 수 있다).",
        cols=[
            C("word_id", "INTEGER", "NOT NULL", "zh_words.id"),
            C("ord", "INTEGER", "NOT NULL", "풀이 순서 (0부터)."),
            C("ko", "TEXT", "", "한국어 풀이 (AI 번역). 없으면 빈 칸."),
            C("en", "TEXT", "NOT NULL", "CC-CEDICT 영어 풀이 원문."),
        ],
    ),
    dict(
        name="ko_zh_links",
        origin="이 저장소가 더한 연결",
        title="같은 한자 표기의 한·중 낱말 연결",
        desc="ko_words.hanja 와 zh_words.traditional 이 같은 쌍 (자형 정규화 후보 포함).",
        cols=[
            C("ko_word_id", "INTEGER", "NOT NULL", "ko_words.id"),
            C("zh_word_id", "INTEGER", "NOT NULL", "zh_words.id"),
        ],
        pk=("ko_word_id", "zh_word_id"),
    ),
    dict(
        name="ko_char_words",
        origin="이 저장소가 더한 연결",
        title="한자 → 한국어 낱말 역색인",
        desc="낱말 원어에 든 한자마다 그 낱말을 가리킨다.",
        cols=[
            C("char", "TEXT", "NOT NULL", "한자 한 글자."),
            C("word_id", "INTEGER", "NOT NULL", "ko_words.id"),
        ],
    ),
    dict(
        name="zh_char_words",
        origin="이 저장소가 더한 연결",
        title="한자 → 중국어 낱말 역색인",
        desc="표제에 든 글자마다 그 낱말을 가리킨다 (간체·번체 글자 둘 다).",
        cols=[
            C("char", "TEXT", "NOT NULL", "한자 한 글자."),
            C("word_id", "INTEGER", "NOT NULL", "zh_words.id"),
        ],
    ),
    dict(
        name="notes",
        origin="AI 집필 (이 저장소, CC BY-SA 4.0)",
        title="985개 한·중 비교 해설",
        desc="한국어 낱말과 중국어 낱말의 비교 해설과 예문 985건. AI 가 썼고 사람이 검수하기 전이라 틀린 곳이 있을 수 있다. "
             "녹음 경로는 뺐다 (녹음 파일은 이 저장소에 없다).",
        cols=[
            C("ko_word_id", "INTEGER", "", "ko_words.id"),
            C("zh_word_id", "INTEGER", "", "zh_words.id"),
            C("pilot_id", "TEXT", "NOT NULL", "해설 번호 (H001 …)."),
            C("relation", "TEXT", "NOT NULL", "equivalent(대응) | overlap(일부 겹침) | contrast(대조)."),
            C("comparison", "TEXT", "NOT NULL", "비교 해설 (한국어)."),
            C("zh_definition", "TEXT", "NOT NULL", "비교에 쓴 중국어 뜻 (한국어)."),
            C("examples", "TEXT", "NOT NULL", "예문 JSON 배열: [{zh, pinyin, ko}, …]."),
        ],
    ),
    dict(
        name="glyphs",
        origin="Unicode Unihan",
        title="한자 글자 정보",
        desc="낱말 표제·이체 관계에 나오는 글자의 Unihan 정보 (kHangul · kMandarin · kDefinition · kTotalStrokes · kRSUnicode). "
             "한국어문회 배정한자(약 6천 자)는 뺐으므로 그 글자들은 이 표에 없다.",
        cols=[
            C("char", "TEXT", "PRIMARY KEY", "한자 한 글자."),
            C("reading", "TEXT", "", "한글 음 (kHangul 의 음절, 여럿이면 공백으로). 없으면 빈 칸."),
            C("pinyin", "TEXT", "", "병음 (kMandarin)."),
            C("en_def", "TEXT", "", "영어 뜻 (kDefinition)."),
            C("stroke_count", "INTEGER", "", "총획수 (kTotalStrokes 첫 값)."),
            C("radical", "TEXT", "", "부수 글자 (kRSUnicode 의 부수 번호를 강희부수 글자로 바꾼 것)."),
        ],
    ),
    dict(
        name="char_variants",
        origin="Unicode Unihan · CC-CEDICT",
        title="글자 사이 이체 관계",
        desc="양방향으로 넣었다 (A의 간체가 B면 (A,B,간체)와 (B,A,번체)). source 가 unihan 또는 cedict 인 행만 든다.",
        cols=[
            C("char", "TEXT", "NOT NULL", "글자."),
            C("variant", "TEXT", "NOT NULL", "관계 있는 글자."),
            C("kind", "TEXT", "NOT NULL", "간체 · 번체 · 이체자 · 일부 뜻 이체 · 자형 차이 · 고자 · 금자 · 일본 자형 (앱 화면에 그대로 보이는 말)."),
            C("source", "TEXT", "NOT NULL", "unihan (kSimplifiedVariant 등 Unihan 변이 항목) | cedict (CC-CEDICT 의 'variant of' 한 글자 표제)."),
        ],
        pk=("char", "variant", "kind"),
    ),
]

TABLE_BY_NAME = {t["name"]: t for t in TABLES}

# 앱 dict.db 에서 가져올 때 쓰는 조건 (그 밖에는 전부)
SRC_FILTER = {"char_variants": "source IN ('unihan', 'cedict')"}

# 공개 SQLite 에 만들 색인 (앱 색인 중 남는 것 + 표제 찾기용 몇 개)
INDEXES = [
    "CREATE INDEX idx_ko_words_headword ON ko_words(headword)",
    "CREATE INDEX idx_ko_words_hanja ON ko_words(hanja)",
    "CREATE INDEX idx_ko_senses_word ON ko_senses(word_id)",
    "CREATE INDEX idx_ko_zh_equivs_word ON ko_zh_equivs(word_id)",
    "CREATE INDEX idx_ko_zh_equivs_zh ON ko_zh_equivs(zh_word_id)",
    "CREATE INDEX idx_ko_synonyms_syn ON ko_synonyms(syn_id)",
    "CREATE INDEX idx_zh_words_simplified ON zh_words(simplified)",
    "CREATE INDEX idx_zh_words_traditional ON zh_words(traditional)",
    "CREATE INDEX idx_zh_senses_word ON zh_senses(word_id)",
    "CREATE INDEX idx_ko_zh_links_zh ON ko_zh_links(zh_word_id)",
    "CREATE INDEX idx_ko_char_words_char ON ko_char_words(char)",
    "CREATE INDEX idx_ko_char_words_word ON ko_char_words(word_id)",
    "CREATE INDEX idx_zh_char_words_char ON zh_char_words(char)",
    "CREATE INDEX idx_zh_char_words_word ON zh_char_words(word_id)",
    "CREATE INDEX idx_notes_ko ON notes(ko_word_id)",
    "CREATE INDEX idx_notes_zh ON notes(zh_word_id)",
    "CREATE INDEX idx_char_variants_char ON char_variants(char)",
]


def ddl_for(t):
    parts = []
    for name, typ, cons, _ in t["cols"]:
        parts.append(f"  {name} {typ}{(' ' + cons) if cons else ''}")
    if t.get("pk"):
        parts.append(f"  PRIMARY KEY ({', '.join(t['pk'])})")
    return f"CREATE TABLE {t['name']} (\n" + ",\n".join(parts) + "\n)"


META_DDL = "CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)"


def schema_sql():
    out = ["-- hanjadict-data 공개 SQLite 스키마 (export_public.py 가 만든다)", ""]
    out.append(META_DDL + ";")
    for t in TABLES:
        out.append(ddl_for(t) + ";")
    out.extend(i + ";" for i in INDEXES)
    return "\n".join(out) + "\n"


def nullable_columns(t):
    return [c[0] for c in t["cols"] if "NOT NULL" not in c[2] and "PRIMARY KEY" not in c[2]]


# ---------------------------------------------------------------------------
# 원본 읽기 · 공개 SQLite 만들기
# ---------------------------------------------------------------------------

def open_source(path):
    uri = "file:" + path + "?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    con.execute("PRAGMA query_only=ON")
    return con


def src_columns(con, table):
    return [r[1] for r in con.execute(f"PRAGMA table_info({table})")]


def notes_clean_examples(raw):
    """examples JSON 에서 녹음 경로 키를 뺀다."""
    items = json.loads(raw)
    for it in items:
        it.pop(NOTES_AUDIO_KEY, None)
    return json.dumps(items, ensure_ascii=False)


def build_public_db(src, out_path, dataset_version, built_at):
    if os.path.exists(out_path):
        os.remove(out_path)
    dst = sqlite3.connect(out_path)
    dst.execute("PRAGMA journal_mode=OFF")
    dst.execute("PRAGMA synchronous=OFF")
    dst.execute(META_DDL)
    for t in TABLES:
        dst.execute(ddl_for(t))
    counts = {}
    src.execute("BEGIN")  # 한 시점의 읽기 스냅샷
    for t in TABLES:
        cols = [c[0] for c in t["cols"]]
        have = set(src_columns(src, t["name"]))
        missing = [c for c in cols if c not in have]
        if missing:
            raise SystemExit(f"원본 {t['name']} 에 열이 없다: {missing}")
        where = SRC_FILTER.get(t["name"])
        sql = f"SELECT {', '.join(cols)} FROM {t['name']}" + (f" WHERE {where}" if where else "") + " ORDER BY rowid"
        ph = ", ".join("?" for _ in cols)
        ins = f"INSERT INTO {t['name']} ({', '.join(cols)}) VALUES ({ph})"
        cur = src.execute(sql)
        ex_idx = cols.index("examples") if t["name"] == "notes" else -1
        batch = []
        n = 0
        for row in cur:
            if ex_idx >= 0:
                row = list(row)
                row[ex_idx] = notes_clean_examples(row[ex_idx])
            batch.append(row)
            n += 1
            if len(batch) >= 50000:
                dst.executemany(ins, batch)
                batch = []
        if batch:
            dst.executemany(ins, batch)
        counts[t["name"]] = n
    src_meta = dict(src.execute("SELECT key, value FROM meta"))
    src.execute("ROLLBACK")

    for i in INDEXES:
        dst.execute(i)
    dst.executemany("INSERT INTO meta (key, value) VALUES (?, ?)", public_meta(src_meta, counts, dataset_version, built_at))
    dst.commit()
    dst.execute("VACUUM")
    dst.close()
    return counts


def public_meta(sm, counts, dataset_version, built_at):
    """공개용 meta. 빌드 경로 같은 내부 정보는 옮기지 않는다 (판 · 만든 날 · 표별 건수 · 원자료 판만)."""
    rows = [
        ("dataset", DATASET_NAME),
        ("dataset_version", dataset_version),
        ("schema_version", PUBLIC_SCHEMA_VERSION),
        ("built_at", built_at),
        ("license", LICENSE_ID),
        ("exporter", "export_public.py"),
    ]
    for t in TABLES:
        rows.append((f"count.{t['name']}", str(counts[t["name"]])))

    def js(key):
        try:
            return json.loads(sm[key])
        except (KeyError, ValueError):
            return None

    def digest(files):
        h = hashlib.sha256()
        for name in sorted(files):
            h.update(f"{name}:{files[name]}\n".encode())
        return h.hexdigest()

    rows.append(("source.stdict", "국립국어원 표준국어대사전 (CC BY-SA 2.0 KR)"))
    f = js("native.stdict.files.sha256")
    if f:
        rows.append(("source.stdict.files", str(len(f))))
        rows.append(("source.stdict.files_digest_sha256", digest(f)))
    rows.append(("source.krdict", "국립국어원 한국어기초사전 (CC BY-SA 2.0 KR)"))
    f = js("input.krdict.files.sha256")
    if f:
        rows.append(("source.krdict.files", str(len(f))))
        rows.append(("source.krdict.files_digest_sha256", digest(f)))
    rows.append(("source.cedict", "CC-CEDICT (CC BY-SA 4.0)"))
    if "input.cedict.sha256" in sm:
        rows.append(("source.cedict.sha256", sm["input.cedict.sha256"]))
    if "count.cedict.entries" in sm:
        rows.append(("source.cedict.entries", sm["count.cedict.entries"]))
    rows.append(("source.cedict_ko", "CC-CEDICT 영어 풀이의 한국어 번역 (AI, CC BY-SA 4.0 2차 저작물)"))
    if "input.cedict_ko.sha256" in sm:
        rows.append(("source.cedict_ko.sha256", sm["input.cedict_ko.sha256"]))
    rows.append(("source.unihan", "Unicode Unihan Database (Unicode License v3)"))
    if "input.unihan.sha256" in sm:
        rows.append(("source.unihan.sha256", sm["input.unihan.sha256"]))
    if "input.hsk30.sha256" in sm:
        rows.append(("source.hsk30.sha256", sm["input.hsk30.sha256"]))
    return rows


# ---------------------------------------------------------------------------
# TSV
# ---------------------------------------------------------------------------

_ESC = {"\\": "\\\\", "\t": "\\t", "\n": "\\n", "\r": "\\r"}
_ESC_RE = re.compile(r"[\\\t\n\r]")
_UNESC = {"\\\\": "\\", "\\t": "\t", "\\n": "\n", "\\r": "\r"}
_UNESC_RE = re.compile(r"\\[\\tnr]")


def tsv_cell(v):
    if v is None:
        return ""
    s = v if isinstance(v, str) else str(v)
    return _ESC_RE.sub(lambda m: _ESC[m.group(0)], s)


def tsv_unescape(s):
    return _UNESC_RE.sub(lambda m: _UNESC[m.group(0)], s)


def table_columns(name):
    if name == "meta":
        return ["key", "value"]
    return [c[0] for c in TABLE_BY_NAME[name]["cols"]]


def write_tsv(db_path, tsv_dir):
    os.makedirs(tsv_dir, exist_ok=True)
    con = sqlite3.connect(db_path)
    sizes = {}
    for name in [t["name"] for t in TABLES] + ["meta"]:
        cols = table_columns(name)
        p = os.path.join(tsv_dir, name + ".tsv")
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write("\t".join(cols) + "\n")
            for row in con.execute(f"SELECT {', '.join(cols)} FROM {name} ORDER BY rowid"):
                f.write("\t".join(tsv_cell(v) for v in row) + "\n")
        sizes[name] = os.path.getsize(p)
    con.close()
    return sizes


# ---------------------------------------------------------------------------
# 공개 저장소에 쓰는 문서 조각
# ---------------------------------------------------------------------------

def fmt(n):
    return f"{n:,}"


def counts_block(counts):
    lines = ["| 표 | 건수 | 원 저작물 | 내용 |", "|---|---:|---|---|"]
    for t in TABLES:
        lines.append(f"| `{t['name']}` | {fmt(counts[t['name']])} | {t['origin']} | {t['title']} |")
    return "\n".join(lines)


def schema_md(counts, meta_rows):
    meta = dict(meta_rows)
    o = []
    o.append("# 표 구조 (Schema)")
    o.append("")
    o.append(f"공개본 판 `{meta['dataset_version']}` (만든 날 {meta['built_at']}), 공개용 스키마 판 `{meta['schema_version']}`. "
             "이 문서는 `tools/export_public.py` 가 만든다. 같은 구조가 `schema.sql` (SQLite DDL)에 있다.")
    o.append("")
    o.append("각 표는 SQLite 파일 안의 표이면서 `tsv/<표>.tsv` 한 파일이다. TSV 는 UTF-8, 머리줄 있음, 칸은 탭으로 나눈다. "
             "칸 안의 탭·줄바꿈·역슬래시는 `\\t` `\\n` `\\r` `\\\\` 로 적고, NULL 은 빈 칸이다. "
             "NULL 이 될 수 있는 열에는 빈 문자열이 없으므로 빈 칸은 항상 NULL 이다 "
             "(NOT NULL 열의 빈 칸은 빈 문자열이다: 고유어의 `ko_words.hanja`).")
    o.append("")
    o.append("## 한눈에")
    o.append("")
    o.append(counts_block(counts))
    o.append("")
    o.append("`meta` 표(키-값)는 판 · 만든 날 · 표별 건수 · 원자료 판을 담는다.")
    o.append("")
    o.append("## 관계")
    o.append("")
    o.append("```")
    o.append("ko_words.id  <- ko_senses.word_id, ko_zh_equivs.word_id, ko_synonyms.word_id / syn_id,")
    o.append("                ko_zh_links.ko_word_id, ko_char_words.word_id, notes.ko_word_id")
    o.append("zh_words.id  <- zh_senses.word_id, ko_zh_equivs.zh_word_id, ko_zh_links.zh_word_id,")
    o.append("                zh_char_words.word_id, notes.zh_word_id")
    o.append("글자 (char)  <- ko_char_words.char, zh_char_words.char, glyphs.char, char_variants.char / variant")
    o.append("```")
    o.append("")
    for t in TABLES:
        o.append(f"## `{t['name']}` — {t['title']}")
        o.append("")
        o.append(f"- 건수: {fmt(counts[t['name']])}")
        o.append(f"- 원 저작물: {t['origin']}")
        o.append(f"- 파일: `tsv/{t['name']}.tsv`")
        o.append("")
        o.append(t["desc"])
        o.append("")
        o.append("| 열 | 형 | 설명 |")
        o.append("|---|---|---|")
        for name, typ, cons, doc in t["cols"]:
            tag = []
            if "PRIMARY KEY" in cons:
                tag.append("PK")
            if t.get("pk") and name in t["pk"]:
                tag.append("PK")
            tag_s = (" (" + ", ".join(dict.fromkeys(tag)) + ")") if tag else ""
            o.append(f"| `{name}`{tag_s} | {typ} | {doc} |")
        if t.get("pk"):
            o.append("")
            o.append(f"기본키: ({', '.join(t['pk'])})")
        o.append("")
    o.append("## `meta` — 공개본 정보")
    o.append("")
    o.append("| 키 | 값 |")
    o.append("|---|---|")
    for k, v in meta_rows:
        o.append(f"| `{k}` | {v} |")
    o.append("")
    o.append("## 색인 (SQLite)")
    o.append("")
    o.append("조회에 쓰라고 아래 색인을 만들어 두었다. 자료가 아니라 색인이므로 필요 없으면 지워도 된다.")
    o.append("")
    o.append("```sql")
    o.extend(i + ";" for i in INDEXES)
    o.append("```")
    o.append("")
    return "\n".join(o)


COUNTS_BEGIN = "<!-- counts:begin -->"
COUNTS_END = "<!-- counts:end -->"


def update_readme_counts(readme_path, counts):
    if not os.path.exists(readme_path):
        return False
    s = open(readme_path, encoding="utf-8").read()
    if COUNTS_BEGIN not in s or COUNTS_END not in s:
        return False
    a = s.index(COUNTS_BEGIN) + len(COUNTS_BEGIN)
    b = s.index(COUNTS_END)
    s = s[:a] + "\n" + counts_block(counts) + "\n" + s[b:]
    open(readme_path, "w", encoding="utf-8").write(s)
    return True


def write_samples(tsv_dir, repo):
    sdir = os.path.join(repo, "samples")
    if os.path.isdir(sdir):
        shutil.rmtree(sdir)
    os.makedirs(sdir)
    for name in [t["name"] for t in TABLES] + ["meta"]:
        src_p = os.path.join(tsv_dir, name + ".tsv")
        with open(src_p, encoding="utf-8", newline="") as f, \
                open(os.path.join(sdir, name + ".tsv"), "w", encoding="utf-8", newline="") as g:
            n = 0 if name != "meta" else -(10 ** 9)  # meta 는 통째로
            for line in f:
                g.write(line)
                n += 1
                if n >= SAMPLE_ROWS + 1:  # 머리줄 + 표본
                    break


# ---------------------------------------------------------------------------
# 공개본 검사
# ---------------------------------------------------------------------------

def row_hash(con, table, cols, where=None, transform=None):
    h = hashlib.sha256()
    n = 0
    sql = f"SELECT {', '.join(cols)} FROM {table}" + (f" WHERE {where}" if where else "") + " ORDER BY rowid"
    for row in con.execute(sql):
        if transform:
            row = transform(row)
        h.update(repr(tuple(row)).encode("utf-8"))
        n += 1
    return n, h.hexdigest()


def verify(src_path, db_path, tsv_dir, repo=None):
    fails = []
    oks = []

    def ok(msg):
        oks.append(msg)

    def bad(msg):
        fails.append(msg)

    pub = sqlite3.connect(db_path)
    src = open_source(src_path)

    # 1. 표 · 열 이름
    tables = {r[0] for r in pub.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    expect = {t["name"] for t in TABLES} | {"meta"}
    if tables == expect:
        ok(f"표 {len(tables)}개가 정의와 같다")
    else:
        bad(f"표 목록 불일치: 더 있음 {sorted(tables - expect)}, 없음 {sorted(expect - tables)}")
    for ft in FORBIDDEN_TABLES:
        if ft in tables:
            bad(f"뺄 표가 있다: {ft}")
    if not [x for x in FORBIDDEN_TABLES if x in tables]:
        ok("characters · search_keys · zh_audio 표가 없다")
    colnames = set()
    for t in tables:
        for r in pub.execute(f"PRAGMA table_info({t})"):
            colnames.add(r[1])
    badcols = [c for c in FORBIDDEN_COLUMNS if c in colnames]
    if badcols:
        bad(f"뺄 열 이름이 있다: {badcols}")
    else:
        ok("어문회 표·녹음 경로 열 이름(level_code, level_label, long_sound, audio_word, path)이 없다")
    if any(n.startswith("sqlite_stat") for n in tables):
        bad("sqlite_stat 표가 있다 (색인 표본이 들어간다)")
    else:
        ok("sqlite_stat 표가 없다")

    # 2. 건수 · 내용 일치
    for t in TABLES:
        name = t["name"]
        cols = [c[0] for c in t["cols"]]
        where = SRC_FILTER.get(name)
        if name == "notes":
            def tr(row, i=cols.index("examples")):
                row = list(row)
                row[i] = notes_clean_examples(row[i])
                return row
        else:
            tr = None
        n_src, h_src = row_hash(src, name, cols, where, tr)
        n_pub, h_pub = row_hash(pub, name, cols)
        if n_src == n_pub and h_src == h_pub:
            ok(f"{name}: 원본 {fmt(n_src)} = 공개 {fmt(n_pub)}, 내용 해시 일치")
        else:
            bad(f"{name}: 원본 {n_src} / 공개 {n_pub}, 해시 {'일치' if h_src == h_pub else '불일치'}")
    # char_variants 는 빠진 행이 정확히 eomunhoe 행인지
    tot = src.execute("SELECT COUNT(*) FROM char_variants").fetchone()[0]
    eo = src.execute("SELECT COUNT(*) FROM char_variants WHERE source='eomunhoe'").fetchone()[0]
    oth = src.execute("SELECT COUNT(*) FROM char_variants WHERE source NOT IN ('unihan','cedict','eomunhoe')").fetchone()[0]
    pubn = pub.execute("SELECT COUNT(*) FROM char_variants").fetchone()[0]
    srcs = {r[0] for r in pub.execute("SELECT DISTINCT source FROM char_variants")}
    if oth == 0 and tot - eo == pubn and srcs <= {"unihan", "cedict"}:
        ok(f"char_variants: 원본 {fmt(tot)} - eomunhoe {fmt(eo)} = 공개 {fmt(pubn)}, source={sorted(srcs)}")
    else:
        bad(f"char_variants 불일치: 원본 {tot}, eomunhoe {eo}, 기타 {oth}, 공개 {pubn}, source {srcs}")

    # 3. 글자열 전수 검사: 모든 표의 모든 텍스트 칸
    hit = {}
    for t in tables:
        cols = [r[1] for r in pub.execute(f"PRAGMA table_info({t})")]
        for c in cols:
            for pat in FORBIDDEN_TEXT:
                n = pub.execute(f"SELECT COUNT(*) FROM {t} WHERE typeof({c})='text' AND instr({c}, ?) > 0", (pat,)).fetchone()[0]
                if n:
                    hit[(t, c, pat)] = n
    n_audio = pub.execute("SELECT COUNT(*) FROM notes WHERE instr(examples, '\"audio\"') > 0 OR instr(examples, '.m4a') > 0").fetchone()[0]
    if n_audio:
        hit[("notes", "examples", "audio")] = n_audio
    if hit:
        bad(f"금지 문자열이 들어 있다: {hit}")
    else:
        ok(f"모든 표의 모든 텍스트 칸에 금지 문자열({', '.join(FORBIDDEN_TEXT)}, 녹음 경로)이 없다")

    # 4. 파일 바이트 검사 (지운 페이지 찌꺼기 포함)
    def scan_bytes(path):
        needles = [LOCAL_PATH.encode(), b"eomunhoe", b"search_keys", b"zh_audio", b"level_label"]
        found = set()
        with open(path, "rb") as f:
            tail = b""
            while True:
                chunk = f.read(1 << 24)
                if not chunk:
                    break
                buf = tail + chunk
                for nd in needles:
                    if nd in buf:
                        found.add(nd.decode())
                tail = buf[-32:]
        return found

    f = scan_bytes(db_path)
    if f:
        bad(f"SQLite 파일 바이트에 금지 문자열: {sorted(f)}")
    else:
        ok("SQLite 파일 바이트 전체에 로컬 경로·eomunhoe·search_keys·zh_audio·level_label 이 없다")
    tsv_found = {}
    for fn in sorted(os.listdir(tsv_dir)):
        r = scan_bytes(os.path.join(tsv_dir, fn))
        if r:
            tsv_found[fn] = sorted(r)
    if tsv_found:
        bad(f"TSV 에 금지 문자열: {tsv_found}")
    else:
        ok("TSV 파일 전체에 같은 금지 문자열이 없다")

    # 5. NULL 이 될 수 있는 열에 빈 문자열이 없는가 (TSV 에서 빈 칸 = NULL 이 되려면)
    amb = []
    for t in TABLES:
        for c in nullable_columns(t):
            n = pub.execute(f"SELECT COUNT(*) FROM {t['name']} WHERE {c} = ''").fetchone()[0]
            if n:
                amb.append((t["name"], c, n))
    if amb:
        bad(f"NULL 가능 열에 빈 문자열: {amb}")
    else:
        ok("NULL 가능 열에는 빈 문자열이 없다 (TSV 빈 칸은 NULL 로 되돌릴 수 있다)")

    # 6. TSV 왕복: TSV 를 다시 읽어 SQLite 행과 칸 단위로 비교
    for name in [t["name"] for t in TABLES] + ["meta"]:
        cols = table_columns(name)
        p = os.path.join(tsv_dir, name + ".tsv")
        mism = 0
        n = 0
        with open(p, encoding="utf-8", newline="") as f:
            header = f.readline().rstrip("\n").split("\t")
            if header != cols:
                bad(f"{name}.tsv 머리줄 불일치")
                continue
            cur = pub.execute(f"SELECT {', '.join(cols)} FROM {name} ORDER BY rowid")
            for line, row in zip(f, cur):
                parts = line[:-1].split("\t")
                n += 1
                if len(parts) != len(cols):
                    mism += 1
                    continue
                for cell, v in zip(parts, row):
                    got = tsv_unescape(cell)
                    want = "" if v is None else str(v)
                    if got != want:
                        mism += 1
                        break
            total = pub.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            if n != total:
                mism += abs(total - n)
        if mism:
            bad(f"{name}.tsv 왕복 불일치 {mism}행 (읽은 {n}행 / SQLite {total}행)")
    if not [x for x in fails if x.endswith("머리줄 불일치") or "왕복" in x]:
        ok("TSV 13개를 다시 읽어 SQLite 와 칸 단위로 비교: 전부 일치 (건수 포함)")

    # 7. meta
    m = dict(pub.execute("SELECT key, value FROM meta"))
    leaks = [k for k, v in m.items() if LOCAL_PATH in v or ".path" in k]
    if leaks:
        bad(f"meta 에 경로성 항목: {leaks}")
    else:
        ok("meta 에 경로·내부 정보가 없다")
    for t in TABLES:
        if m.get(f"count.{t['name']}") != str(pub.execute(f"SELECT COUNT(*) FROM {t['name']}").fetchone()[0]):
            bad(f"meta count.{t['name']} 불일치")

    # 8. 공개 저장소 파일 전체에서 로컬 경로
    if repo:
        offenders = []
        for root, dirs, files in os.walk(repo):
            dirs[:] = [d for d in dirs if d not in (".git", "dist")]
            for fn in files:
                p = os.path.join(root, fn)
                try:
                    data = open(p, "rb").read()
                except OSError:
                    continue
                rel = os.path.relpath(p, repo)
                # tools/ 의 이 스크립트는 검사 대상 문자열을 상수로 갖고 있으므로 eomunhoe 검사에서만 뺀다
                if LOCAL_PATH.encode() in data or (b"eomunhoe" in data and not rel.startswith("tools" + os.sep)):
                    offenders.append(rel)
        if offenders:
            bad(f"저장소 파일에 로컬 경로·eomunhoe: {offenders}")
        else:
            ok("저장소 파일(.git·dist 제외)에 로컬 경로·eomunhoe 가 없다")

    pub.close()
    src.close()
    return oks, fails


# ---------------------------------------------------------------------------
# 압축본
# ---------------------------------------------------------------------------

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def make_dist(db_path, tsv_dir, dist, version):
    os.makedirs(dist, exist_ok=True)
    base = f"{DATASET_NAME}-{version}"
    outs = []

    def run(cmd, stdout=None):
        subprocess.run(cmd, check=True, stdout=stdout)

    # SQLite
    for ext, cmd in (("zst", ["zstd", "-19", "-T0", "-q", "-f"]), ("gz", ["gzip", "-9", "-n", "-f"])):
        target = os.path.join(dist, f"{base}.sqlite.{ext}")
        if shutil.which(cmd[0]) is None:
            print(f"  ({cmd[0]} 없음, 건너뜀)")
            continue
        with open(target, "wb") as o:
            if ext == "zst":
                run(cmd + ["-c", db_path], stdout=o)
            else:
                run(cmd + ["-c", db_path], stdout=o)
        outs.append(target)
    # TSV 묶음 (표 13개를 한 tar 로 — 결정적 순서·고정 mtime)
    tar_path = os.path.join(dist, f"{base}-tsv.tar")
    with tarfile.open(tar_path, "w", format=tarfile.PAX_FORMAT) as tf:
        for fn in sorted(os.listdir(tsv_dir)):
            ti = tf.gettarinfo(os.path.join(tsv_dir, fn), arcname=f"{base}-tsv/{fn}")
            ti.uid = ti.gid = 0
            ti.uname = ti.gname = ""
            ti.mtime = 0
            ti.mode = 0o644
            with open(os.path.join(tsv_dir, fn), "rb") as f:
                tf.addfile(ti, f)
    for ext, cmd in (("zst", ["zstd", "-19", "-T0", "-q", "-f"]), ("gz", ["gzip", "-9", "-n", "-f"])):
        target = tar_path + "." + ext
        if shutil.which(cmd[0]) is None:
            continue
        with open(target, "wb") as o:
            run(cmd + ["-c", tar_path], stdout=o)
        outs.append(target)
    os.remove(tar_path)
    sums = os.path.join(dist, "SHA256SUMS")
    with open(sums, "w", encoding="utf-8") as f:
        for p in sorted(outs):
            f.write(f"{sha256_file(p)}  {os.path.basename(p)}\n")
    return outs + [sums]


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--db", default=DEFAULT_DB, help="앱 dict.db (읽기 전용으로만 연다)")
    ap.add_argument("--out", required=True, help="결과를 쓸 디렉터리 (hanjadict-data.sqlite · tsv/)")
    ap.add_argument("--repo", help="공개 저장소 디렉터리 (schema.sql · SCHEMA.md · samples/ · README 건수 · tools/)")
    ap.add_argument("--dist", help="압축본을 둘 디렉터리 (GitHub Releases 용)")
    ap.add_argument("--version", help="공개본 판 이름 (기본: 오늘 날짜 YYYY.MM.DD)")
    args = ap.parse_args()

    now = datetime.datetime.now().astimezone()
    version = args.version or now.strftime("%Y.%m.%d")
    built_at = now.isoformat(timespec="seconds")
    db_abs = os.path.abspath(args.db)
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    pub_db = os.path.join(out, DATASET_NAME + ".sqlite")
    tsv_dir = os.path.join(out, "tsv")
    if os.path.isdir(tsv_dir):
        shutil.rmtree(tsv_dir)

    print(f"원본(읽기 전용): {db_abs}")
    src = open_source(db_abs)
    counts = build_public_db(src, pub_db, version, built_at)
    src.close()
    print(f"공개 SQLite: {pub_db} ({os.path.getsize(pub_db):,} bytes)")
    sizes = write_tsv(pub_db, tsv_dir)
    print(f"TSV: {tsv_dir} ({sum(sizes.values()):,} bytes, 파일 {len(sizes)}개)")

    pub = sqlite3.connect(pub_db)
    meta_rows = list(pub.execute("SELECT key, value FROM meta ORDER BY rowid"))
    pub.close()

    repo = os.path.abspath(args.repo) if args.repo else None
    if repo:
        os.makedirs(repo, exist_ok=True)
        open(os.path.join(repo, "schema.sql"), "w", encoding="utf-8").write(schema_sql())
        open(os.path.join(repo, "SCHEMA.md"), "w", encoding="utf-8").write(schema_md(counts, meta_rows))
        write_samples(tsv_dir, repo)
        os.makedirs(os.path.join(repo, "tools"), exist_ok=True)
        tool_dst = os.path.join(repo, "tools", "export_public.py")
        if os.path.abspath(__file__) != os.path.abspath(tool_dst):  # 저장소 안의 사본으로 돌릴 때는 자기 자신이다
            shutil.copyfile(os.path.abspath(__file__), tool_dst)
        updated = update_readme_counts(os.path.join(repo, "README.md"), counts)
        print(f"저장소 갱신: schema.sql SCHEMA.md samples/ tools/ README건수={'갱신' if updated else '표지 없음'}")

    if args.dist:
        print("압축본 만드는 중 ...")
        for p in make_dist(pub_db, tsv_dir, os.path.abspath(args.dist), version):
            print(f"  {os.path.basename(p)}  {os.path.getsize(p):,} bytes")

    oks, fails = verify(db_abs, pub_db, tsv_dir, repo)
    print("\n공개본 검사")
    for m in oks:
        print("  [통과]", m)
    for m in fails:
        print("  [실패]", m)
    if fails:
        sys.exit(1)
    print("\n검사 전부 통과")


if __name__ == "__main__":
    main()
