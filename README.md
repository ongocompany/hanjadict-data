# 한중종합사전 사전 데이터

한국어 한자사전과 중국어 사전을 한데 묶은 앱 **한중종합사전**이 쓰는 사전 데이터입니다.
한국어 낱말(표준국어대사전·한국어기초사전)과 중국어 낱말(CC-CEDICT)을 같은 한자로 잇고,
한자 글자 정보(Unicode Unihan)와 한·중 비교 해설 985건을 더했습니다.

앱: **한중종합사전** — App Store·Google Play·Microsoft Store 출시 준비 중

이 자료는 CC BY-SA 원 저작물로 만들었으므로 **전체를 CC BY-SA 4.0 으로 공개**합니다.
(국립국어원 두 사전은 CC BY-SA 2.0 KR 이고, 그 부분은 원 조건도 함께 지킵니다. [ATTRIBUTION.md](ATTRIBUTION.md))

## 무엇이 들어 있나

SQLite 파일 하나, 또는 표마다 TSV 한 개씩(같은 내용). 표 12개와 판 정보(`meta`)입니다.

<!-- counts:begin -->
| 표 | 건수 | 원 저작물 | 내용 |
|---|---:|---|---|
| `ko_words` | 341,773 | 표준국어대사전 · 한국어기초사전 | 한국어 낱말 |
| `ko_senses` | 397,732 | 표준국어대사전 | 한국어 뜻풀이 |
| `ko_zh_equivs` | 82,300 | 한국어기초사전 | 한국어 뜻별 중국어 대응어 |
| `ko_synonyms` | 10,193 | 표준국어대사전 | 고유어의 같은 뜻 한자어 |
| `zh_words` | 124,814 | CC-CEDICT | 중국어 낱말 |
| `zh_senses` | 199,613 | CC-CEDICT · 한국어 풀이는 AI 번역 2차 저작물 | 중국어 풀이 |
| `ko_zh_links` | 34,921 | 이 저장소가 더한 연결 | 같은 한자 표기의 한·중 낱말 연결 |
| `ko_char_words` | 884,174 | 이 저장소가 더한 연결 | 한자 → 한국어 낱말 역색인 |
| `zh_char_words` | 427,601 | 이 저장소가 더한 연결 | 한자 → 중국어 낱말 역색인 |
| `notes` | 985 | AI 집필 (이 저장소, CC BY-SA 4.0) | 985개 한·중 비교 해설 |
| `glyphs` | 16,157 | Unicode Unihan | 한자 글자 정보 |
| `char_variants` | 21,090 | Unicode Unihan · CC-CEDICT | 글자 사이 이체 관계 |
<!-- counts:end -->

열 하나하나의 뜻과 표 사이의 관계는 [SCHEMA.md](SCHEMA.md), SQLite 정의는 [schema.sql](schema.sql) 입니다.

- **한국어 → 중국어**: `ko_words` 의 `id` 에서 `ko_zh_equivs`(한국어기초사전의 중국어 대응어)와 `ko_zh_links`(같은 한자 표기의 중국어 낱말)로 갑니다.
- **고유어 → 한자어**: 고유어(`hanja` 가 빈 문자열)는 `ko_synonyms` 로 같은 뜻 한자어를 찾습니다. 민들레 → 蒲公英 · 地丁 · 金簪草 · 蒲公草.
- **글자 → 낱말**: `ko_char_words`, `zh_char_words` 가 한자 한 글자를 그 글자가 든 낱말로 잇습니다.
- **글자 정보**: `glyphs`(음·병음·영어 뜻·획수·부수), `char_variants`(간체·번체·이체자 관계).
- **비교 해설**: `notes` 의 985건. AI 가 썼습니다.

### 써 보기

```sh
sqlite3 hanjadict-data.sqlite "
  SELECT w.headword, s.hanja
  FROM ko_words w JOIN ko_synonyms y ON y.word_id = w.id JOIN ko_words s ON s.id = y.syn_id
  WHERE w.headword = '민들레' ORDER BY y.ord;"
# 민들레|蒲公英 …

sqlite3 hanjadict-data.sqlite "
  SELECT z.simplified, z.pinyin, s.ko, s.en
  FROM zh_words z JOIN zh_senses s ON s.word_id = z.id
  WHERE z.simplified = '学习' ORDER BY s.ord;"
# 学习|xué xí|배우다; 공부하다|to learn; to study
```

## 어디에 있나 (저장소 · Releases)

데이터가 커서(SQLite 약 170MB, TSV 합 약 105MB) GitHub 의 파일당 100MB 한도를 넘습니다.
그래서 **전체 자료는 [Releases](https://github.com/ongocompany/hanjadict-data/releases) 에서 내려받고**, 이 저장소에는 문서와 작은 표본만 둡니다.

| 파일 | 어디에 | 내용 |
|---|---|---|
| `README.md` `ATTRIBUTION.md` `LICENSE` | 저장소 | 설명 · 출처 · 라이선스 전문 |
| `SCHEMA.md` `schema.sql` | 저장소 | 표 구조 |
| `samples/*.tsv` | 저장소 | 표마다 앞 30행과 `meta` 전체 |
| `docs/` | 저장소 (GitHub Pages) | 앱 개인정보처리방침 · 지원 페이지 |
| `tools/export_public.py` | 저장소 | 이 자료를 내보내고 검사한 스크립트 (그 시점의 사본) |
| `hanjadict-data-<판>.sqlite.zst` / `.gz` | Releases | 전체 SQLite (압축) |
| `hanjadict-data-<판>-tsv.tar.zst` / `.gz` | Releases | 전체 TSV 13개 (압축) |
| `SHA256SUMS` | Releases | 위 파일들의 해시 |

### 내려받는 법

```sh
# 판 이름은 Releases 페이지에서 확인합니다 (예: 2026.10.22)
curl -LO https://github.com/ongocompany/hanjadict-data/releases/download/v2026.10.22/hanjadict-data-2026.10.22.sqlite.zst
curl -LO https://github.com/ongocompany/hanjadict-data/releases/download/v2026.10.22/SHA256SUMS
shasum -a 256 -c --ignore-missing SHA256SUMS
zstd -d hanjadict-data-2026.10.22.sqlite.zst        # → hanjadict-data-2026.10.22.sqlite
```

zstd 가 없으면 `.gz` 를 `gunzip` 으로 풀면 됩니다 (조금 더 큽니다).
TSV 는 `tar -xf hanjadict-data-2026.10.22-tsv.tar.zst` (또는 `tar -xzf …tar.gz`).

TSV 규칙: UTF-8, 머리줄 있음, 탭으로 나눔. 칸 안의 탭·줄바꿈·역슬래시는 `\t` `\n` `\r` `\\`, NULL 은 빈 칸입니다.
TSV 를 고른 까닭은 열이 둘뿐인 큰 표(글자 → 낱말 역색인 88만 행)가 많아 JSONL 은 열 이름을 되풀이하며 훨씬 커지고,
TSV 는 엑셀·pandas·DuckDB 가 바로 읽기 때문입니다.

## 출처별 범위

| 원 저작물 | 라이선스 | 이 자료의 표 |
|---|---|---|
| 표준국어대사전 (국립국어원) | CC BY-SA 2.0 KR | `ko_words` `ko_senses` `ko_synonyms` |
| 한국어기초사전 (국립국어원) | CC BY-SA 2.0 KR | `ko_words.level` · `ko_zh_equivs` |
| CC-CEDICT | CC BY-SA 4.0 | `zh_words` `zh_senses.en` `zh_char_words` · `char_variants` 의 cedict 행 |
| CC-CEDICT 한국어 풀이 (AI 번역, 2차 저작물) | CC BY-SA 4.0 | `zh_senses.ko` |
| 한·중 비교 해설 985건 (AI 집필) | CC BY-SA 4.0 | `notes` |
| Unicode Unihan | Unicode License v3 | `glyphs` · `char_variants` 의 unihan 행 |
| 이 저장소가 더한 연결 | CC BY-SA 4.0 | `ko_zh_links` `ko_char_words` `zh_char_words` |

저작자·링크·우리가 바꾼 것은 [ATTRIBUTION.md](ATTRIBUTION.md) 에 있습니다.

## 빠진 것

- **한국어문회 배정한자 자료.** 앱은 한국어문회 배정한자 약 6천 자의 훈음·급수 등을 쓰지만, 그 자료는 별도의 권리가 있어 이 공개본에 넣지 않습니다. 앱 안에서만 씁니다. 그래서 `glyphs` 에는 그 글자들이 없고, `char_variants` 에서도 그 자료에서 온 관계(동자)는 넣지 않았습니다.
- **녹음 파일.** 앱 안에만 있습니다. `notes` 의 녹음 경로도 뺐습니다.
- **앱 내부용 정보.** 검색용 색인표, 녹음 연결표, 빌드 경로 같은 내부 정보. 공개용 `meta` 는 새로 만들었습니다(판 · 만든 날 · 표별 건수 · 원자료 판).
- 앱 소스 코드는 이 저장소에 없습니다.

## 알아 두실 점

- **AI 가 만든 부분은 사람이 검수하기 전입니다.** `zh_senses.ko`(영어 풀이의 한국어 번역)와 `notes`(비교 해설·예문)는 AI 가 만들었고 틀린 곳이 있을 수 있습니다. 영어 원문을 함께 두었습니다.
- `rank` 는 앱이 목록을 줄 세우는 값입니다. 사전의 권위 있는 순서가 아닙니다.
- `zh_words.hsk` 는 HSK 3.0 등급 값입니다. 표준 문서의 단어표 자체는 싣지 않았습니다.
- `ko_zh_links` 는 한자 표기가 같은 쌍을 기계로 이은 것이라 뜻이 어긋나는 쌍이 있습니다(`notes` 가 그런 경우를 설명합니다).
- 공개본은 앱의 한 시점 자료입니다. 판은 `meta.dataset_version` 에 있습니다.

## 갱신 방법

공개본은 앱 저장소(비공개)의 자료 묶음에서 `tools/export_public.py` 로 내보냅니다. 같은 스크립트가 빠질 것이 정말 빠졌는지,
표별 건수와 내용이 원본과 맞는지, TSV 를 다시 읽어도 SQLite 와 같은지를 검사하고 하나라도 어긋나면 실패합니다.

```sh
python3 tools/export_public.py --db <앱의 dict.db> --out <작업 폴더> --repo . --dist ./dist
```

1. 위 명령이 `schema.sql` `SCHEMA.md` `samples/` 와 이 README 의 건수 표를 갱신하고, `dist/`(gitignore)에 압축본을 만듭니다.
2. 바뀐 문서를 커밋합니다.
3. `dist/` 의 파일을 새 Release(`v<판>`)에 올립니다.

자료의 오류는 Issues 로 알려 주세요: **https://github.com/ongocompany/hanjadict-data/issues**. 고친 내용은 원본 자료를 바로잡은 뒤 다음 판에 반영합니다.

## 라이선스

[Creative Commons 저작자표시-동일조건변경허락 4.0 국제 (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/deed.ko) — 전문은 [LICENSE](LICENSE).

- 쓰실 때는 [ATTRIBUTION.md](ATTRIBUTION.md) 의 원 저작물을 밝혀 주세요. 예: 「국립국어원 표준국어대사전·한국어기초사전, CC-CEDICT, Unicode Unihan 을 바탕으로 한 한중종합사전 사전 데이터 (CC BY-SA 4.0)」
- 이 자료를 고쳐 새 자료를 만들었다면 같은 라이선스로 공개해 주세요. 상업적 이용도 가능합니다.
- `glyphs` 와 `char_variants` 의 unihan 행에는 Unicode License v3 의 고지도 따라옵니다(ATTRIBUTION.md 에 전문).

## 문의

- 연락 이메일: **support@hanjahanja.co.kr**
- 개인정보처리방침·지원 페이지: `docs/` (https://ongocompany.github.io/hanjadict-data/)

---

## About (English)

**Han-Jung Dictionary data** — the dictionary data behind the *Han-Jung Dictionary* (한중종합사전) app, a Korean Hanja dictionary
with a Chinese dictionary built on top. It links Korean words (Standard Korean Dictionary and Basic Korean Dictionary, National
Institute of Korean Language; CC BY-SA 2.0 KR) to Chinese words (CC-CEDICT; CC BY-SA 4.0) through shared Hanja, and adds
character information from the Unicode Unihan Database (Unicode License v3) and 985 Korean–Chinese comparison notes written by AI.
Because it is built from CC BY-SA works, **the whole dataset is released under CC BY-SA 4.0**.

- **Contents**: 12 tables plus `meta`, as one SQLite file or one UTF-8 TSV file per table (same content). Row counts are in the table above; column documentation is in [SCHEMA.md](SCHEMA.md).
- **Download**: the full data is larger than GitHub's 100 MB file limit, so it is attached to [Releases](https://github.com/ongocompany/hanjadict-data/releases) as `.sqlite.zst` / `.gz` and `-tsv.tar.zst` / `.gz` with `SHA256SUMS`. This repository holds documentation, the schema and 30-row samples of every table.
- **Left out**: the Korean Hanja Society (한국어문회) grade/reading data for its roughly 6,000 assigned characters (a separate right; the app uses it internally only), the app's internal search index, audio files and paths, and build information.
- **Caveats**: the Korean glosses of CC-CEDICT entries (`zh_senses.ko`) and the comparison notes (`notes`) are AI-generated and not yet human-reviewed; the English originals are kept next to them. `rank` is an app-internal sort key.
- **Attribution**: please credit the original works listed in [ATTRIBUTION.md](ATTRIBUTION.md); derivative works must be shared under the same license.
- **Contact**: support@hanjahanja.co.kr. **App**: 한중종합사전 (Han-Jung Dictionary), coming to the App Store, Google Play and Microsoft Store.
