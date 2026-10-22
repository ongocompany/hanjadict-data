# 표 구조 (Schema)

공개본 판 `2026.10.22` (만든 날 2026-10-22T20:42:14+09:00), 공개용 스키마 판 `1`. 이 문서는 `tools/export_public.py` 가 만든다. 같은 구조가 `schema.sql` (SQLite DDL)에 있다.

각 표는 SQLite 파일 안의 표이면서 `tsv/<표>.tsv` 한 파일이다. TSV 는 UTF-8, 머리줄 있음, 칸은 탭으로 나눈다. 칸 안의 탭·줄바꿈·역슬래시는 `\t` `\n` `\r` `\\` 로 적고, NULL 은 빈 칸이다. NULL 이 될 수 있는 열에는 빈 문자열이 없으므로 빈 칸은 항상 NULL 이다 (NOT NULL 열의 빈 칸은 빈 문자열이다: 고유어의 `ko_words.hanja`).

## 한눈에

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

`meta` 표(키-값)는 판 · 만든 날 · 표별 건수 · 원자료 판을 담는다.

## 관계

```
ko_words.id  <- ko_senses.word_id, ko_zh_equivs.word_id, ko_synonyms.word_id / syn_id,
                ko_zh_links.ko_word_id, ko_char_words.word_id, notes.ko_word_id
zh_words.id  <- zh_senses.word_id, ko_zh_equivs.zh_word_id, ko_zh_links.zh_word_id,
                zh_char_words.word_id, notes.zh_word_id
글자 (char)  <- ko_char_words.char, zh_char_words.char, glyphs.char, char_variants.char / variant
```

## `ko_words` — 한국어 낱말

- 건수: 341,773
- 원 저작물: 표준국어대사전 · 한국어기초사전
- 파일: `tsv/ko_words.tsv`

표준국어대사전의 한자어·혼종어(원어 한자가 있는 낱말 전부)와, 한자·중국어로 이어지는 고유어. 한국어기초사전의 등급을 붙였다.

| 열 | 형 | 설명 |
|---|---|---|
| `id` (PK) | INTEGER | 낱말 번호. 다른 표가 이 번호로 가리킨다. |
| `headword` | TEXT | 표제어 (예: 신문). 동음이의 번호는 homonym_no 로 떼어 두었다. |
| `homonym_no` | INTEGER | 동음이의어 번호. 없으면 빈 칸. |
| `hanja` | TEXT | 원어 한자 (예: 新聞). 고유어는 빈 문자열. |
| `word_type` | TEXT | 어종: 고유어 · 한자어 · 혼종어 (표준국어대사전). |
| `pos` | TEXT | 품사 (표준국어대사전). 없으면 '품사 없음'. |
| `pronunciation` | TEXT | 발음 (표준국어대사전). ː 는 긴소리. |
| `is_affix` | INTEGER | 접사·어근 따위 붙는 말이면 1. |
| `level` | INTEGER | 한국어기초사전 등급: 1 초급, 2 중급, 3 고급, 4 등급 없이 수록. 미수록은 빈 칸. |
| `rank` | INTEGER | 앱이 목록을 줄 세우는 값 (작을수록 먼저). 등급·중국어 연결·글자 수·동음이의 번호로 만든다. |

## `ko_senses` — 한국어 뜻풀이

- 건수: 397,732
- 원 저작물: 표준국어대사전
- 파일: `tsv/ko_senses.tsv`

ko_words 의 뜻풀이. 낱말 하나에 뜻이 여럿이면 여러 행.

| 열 | 형 | 설명 |
|---|---|---|
| `word_id` | INTEGER | ko_words.id |
| `sense_no` | INTEGER | 뜻 번호. |
| `definition` | TEXT | 뜻풀이 원문 (표준국어대사전). |
| `category` | TEXT | 전문 분야·갈래 표지 (예: 역사). 없으면 빈 칸. |

## `ko_zh_equivs` — 한국어 뜻별 중국어 대응어

- 건수: 82,300
- 원 저작물: 한국어기초사전
- 파일: `tsv/ko_zh_equivs.tsv`

한국어기초사전이 뜻풀이마다 달아 둔 중국어 대응어. 쉼표 · ， · 、 로 나눈 후보 하나가 한 행. ko_words 와 표제+원어(고유어는 표제+품사)로 맞춘 것만 들었다.

| 열 | 형 | 설명 |
|---|---|---|
| `word_id` | INTEGER | ko_words.id |
| `ord` | INTEGER | 보여 줄 순서 (0부터). |
| `ko_definition` | TEXT | 그 대응어가 달린 한국어기초사전 뜻풀이. |
| `zh` | TEXT | 중국어 대응어 한 후보. |
| `zh_word_id` | INTEGER | zh_words 에 같은 간체 표제가 있으면 그 id (여럿이면 rank 가 가장 작은 것). |

## `ko_synonyms` — 고유어의 같은 뜻 한자어

- 건수: 10,193
- 원 저작물: 표준국어대사전
- 파일: `tsv/ko_synonyms.tsv`

고유어 낱말 뜻에 달린 동의어·비슷한말 중 한자어인 것.

| 열 | 형 | 설명 |
|---|---|---|
| `word_id` (PK) | INTEGER | 고유어 ko_words.id |
| `syn_id` (PK) | INTEGER | 한자가 있는 ko_words.id |
| `kind` | TEXT | 동의어 | 비슷한말 |
| `ord` | INTEGER | 보여 줄 순서. |

기본키: (word_id, syn_id)

## `zh_words` — 중국어 낱말

- 건수: 124,814
- 원 저작물: CC-CEDICT
- 파일: `tsv/zh_words.tsv`

CC-CEDICT 표제 전체. HSK 3.0 등급 값을 붙였다.

| 열 | 형 | 설명 |
|---|---|---|
| `id` (PK) | INTEGER | 낱말 번호. |
| `simplified` | TEXT | 간체 표제. |
| `traditional` | TEXT | 번체 표제. |
| `pinyin` | TEXT | 병음 (성조 부호, 음절 사이 공백). |
| `pinyin_num` | TEXT | CC-CEDICT 원문 숫자 성조 병음 (xue2 xi2). |
| `hsk` | INTEGER | HSK 3.0 등급 1..6, 7 은 7-9급. 등급 밖은 빈 칸. |
| `rank` | INTEGER | 앱이 목록을 줄 세우는 값 (작을수록 먼저). |

## `zh_senses` — 중국어 풀이

- 건수: 199,613
- 원 저작물: CC-CEDICT · 한국어 풀이는 AI 번역 2차 저작물
- 파일: `tsv/zh_senses.tsv`

zh_words 의 풀이. en 은 CC-CEDICT 원문, ko 는 그 영어 풀이를 AI 로 한국어로 옮긴 2차 저작물이다 (사람이 검수하기 전이라 틀린 곳이 있을 수 있다).

| 열 | 형 | 설명 |
|---|---|---|
| `word_id` | INTEGER | zh_words.id |
| `ord` | INTEGER | 풀이 순서 (0부터). |
| `ko` | TEXT | 한국어 풀이 (AI 번역). 없으면 빈 칸. |
| `en` | TEXT | CC-CEDICT 영어 풀이 원문. |

## `ko_zh_links` — 같은 한자 표기의 한·중 낱말 연결

- 건수: 34,921
- 원 저작물: 이 저장소가 더한 연결
- 파일: `tsv/ko_zh_links.tsv`

ko_words.hanja 와 zh_words.traditional 이 같은 쌍 (자형 정규화 후보 포함).

| 열 | 형 | 설명 |
|---|---|---|
| `ko_word_id` (PK) | INTEGER | ko_words.id |
| `zh_word_id` (PK) | INTEGER | zh_words.id |

기본키: (ko_word_id, zh_word_id)

## `ko_char_words` — 한자 → 한국어 낱말 역색인

- 건수: 884,174
- 원 저작물: 이 저장소가 더한 연결
- 파일: `tsv/ko_char_words.tsv`

낱말 원어에 든 한자마다 그 낱말을 가리킨다.

| 열 | 형 | 설명 |
|---|---|---|
| `char` | TEXT | 한자 한 글자. |
| `word_id` | INTEGER | ko_words.id |

## `zh_char_words` — 한자 → 중국어 낱말 역색인

- 건수: 427,601
- 원 저작물: 이 저장소가 더한 연결
- 파일: `tsv/zh_char_words.tsv`

표제에 든 글자마다 그 낱말을 가리킨다 (간체·번체 글자 둘 다).

| 열 | 형 | 설명 |
|---|---|---|
| `char` | TEXT | 한자 한 글자. |
| `word_id` | INTEGER | zh_words.id |

## `notes` — 985개 한·중 비교 해설

- 건수: 985
- 원 저작물: AI 집필 (이 저장소, CC BY-SA 4.0)
- 파일: `tsv/notes.tsv`

한국어 낱말과 중국어 낱말의 비교 해설과 예문 985건. AI 가 썼고 사람이 검수하기 전이라 틀린 곳이 있을 수 있다. 녹음 경로는 뺐다 (녹음 파일은 이 저장소에 없다).

| 열 | 형 | 설명 |
|---|---|---|
| `ko_word_id` | INTEGER | ko_words.id |
| `zh_word_id` | INTEGER | zh_words.id |
| `pilot_id` | TEXT | 해설 번호 (H001 …). |
| `relation` | TEXT | equivalent(대응) | overlap(일부 겹침) | contrast(대조). |
| `comparison` | TEXT | 비교 해설 (한국어). |
| `zh_definition` | TEXT | 비교에 쓴 중국어 뜻 (한국어). |
| `examples` | TEXT | 예문 JSON 배열: [{zh, pinyin, ko}, …]. |

## `glyphs` — 한자 글자 정보

- 건수: 16,157
- 원 저작물: Unicode Unihan
- 파일: `tsv/glyphs.tsv`

낱말 표제·이체 관계에 나오는 글자의 Unihan 정보 (kHangul · kMandarin · kDefinition · kTotalStrokes · kRSUnicode). 한국어문회 배정한자(약 6천 자)는 뺐으므로 그 글자들은 이 표에 없다.

| 열 | 형 | 설명 |
|---|---|---|
| `char` (PK) | TEXT | 한자 한 글자. |
| `reading` | TEXT | 한글 음 (kHangul 의 음절, 여럿이면 공백으로). 없으면 빈 칸. |
| `pinyin` | TEXT | 병음 (kMandarin). |
| `en_def` | TEXT | 영어 뜻 (kDefinition). |
| `stroke_count` | INTEGER | 총획수 (kTotalStrokes 첫 값). |
| `radical` | TEXT | 부수 글자 (kRSUnicode 의 부수 번호를 강희부수 글자로 바꾼 것). |

## `char_variants` — 글자 사이 이체 관계

- 건수: 21,090
- 원 저작물: Unicode Unihan · CC-CEDICT
- 파일: `tsv/char_variants.tsv`

양방향으로 넣었다 (A의 간체가 B면 (A,B,간체)와 (B,A,번체)). source 가 unihan 또는 cedict 인 행만 든다.

| 열 | 형 | 설명 |
|---|---|---|
| `char` (PK) | TEXT | 글자. |
| `variant` (PK) | TEXT | 관계 있는 글자. |
| `kind` (PK) | TEXT | 간체 · 번체 · 이체자 · 일부 뜻 이체 · 자형 차이 · 고자 · 금자 · 일본 자형 (앱 화면에 그대로 보이는 말). |
| `source` | TEXT | unihan (kSimplifiedVariant 등 Unihan 변이 항목) | cedict (CC-CEDICT 의 'variant of' 한 글자 표제). |

기본키: (char, variant, kind)

## `meta` — 공개본 정보

| 키 | 값 |
|---|---|
| `dataset` | hanjadict-data |
| `dataset_version` | 2026.10.22 |
| `schema_version` | 1 |
| `built_at` | 2026-10-22T20:42:14+09:00 |
| `license` | CC-BY-SA-4.0 |
| `exporter` | export_public.py |
| `count.ko_words` | 341773 |
| `count.ko_senses` | 397732 |
| `count.ko_zh_equivs` | 82300 |
| `count.ko_synonyms` | 10193 |
| `count.zh_words` | 124814 |
| `count.zh_senses` | 199613 |
| `count.ko_zh_links` | 34921 |
| `count.ko_char_words` | 884174 |
| `count.zh_char_words` | 427601 |
| `count.notes` | 985 |
| `count.glyphs` | 16157 |
| `count.char_variants` | 21090 |
| `source.stdict` | 국립국어원 표준국어대사전 (CC BY-SA 2.0 KR) |
| `source.stdict.files` | 88 |
| `source.stdict.files_digest_sha256` | 6178083b1d5726803240bd26c6cbf88fa6bd2ebe0009bdd2a2771768180b4592 |
| `source.krdict` | 국립국어원 한국어기초사전 (CC BY-SA 2.0 KR) |
| `source.krdict.files` | 11 |
| `source.krdict.files_digest_sha256` | 1f77cdb4df952e00d4dbc1025de40fc3082b9366938ab7c4f17999629c31f7c5 |
| `source.cedict` | CC-CEDICT (CC BY-SA 4.0) |
| `source.cedict.sha256` | cdd661993ff46764184252231bc3bf9b28d2d9460f9f67da45d557371b74884b |
| `source.cedict.entries` | 124814 |
| `source.cedict_ko` | CC-CEDICT 영어 풀이의 한국어 번역 (AI, CC BY-SA 4.0 2차 저작물) |
| `source.cedict_ko.sha256` | 65cfc23721879441765c49dfa6b27e605d37148fe3058e489d06f3e52465efeb |
| `source.unihan` | Unicode Unihan Database (Unicode License v3) |
| `source.unihan.sha256` | f7a48b2b545acfaa77b2d607ae28747404ce02baefee16396c5d2d7a8ef34b5e |
| `source.hsk30.sha256` | 8c2b73f74776240bcf154624730fc6fb2c42c254d5c5d0f88943878b8e575b9b |

## 색인 (SQLite)

조회에 쓰라고 아래 색인을 만들어 두었다. 자료가 아니라 색인이므로 필요 없으면 지워도 된다.

```sql
CREATE INDEX idx_ko_words_headword ON ko_words(headword);
CREATE INDEX idx_ko_words_hanja ON ko_words(hanja);
CREATE INDEX idx_ko_senses_word ON ko_senses(word_id);
CREATE INDEX idx_ko_zh_equivs_word ON ko_zh_equivs(word_id);
CREATE INDEX idx_ko_zh_equivs_zh ON ko_zh_equivs(zh_word_id);
CREATE INDEX idx_ko_synonyms_syn ON ko_synonyms(syn_id);
CREATE INDEX idx_zh_words_simplified ON zh_words(simplified);
CREATE INDEX idx_zh_words_traditional ON zh_words(traditional);
CREATE INDEX idx_zh_senses_word ON zh_senses(word_id);
CREATE INDEX idx_ko_zh_links_zh ON ko_zh_links(zh_word_id);
CREATE INDEX idx_ko_char_words_char ON ko_char_words(char);
CREATE INDEX idx_ko_char_words_word ON ko_char_words(word_id);
CREATE INDEX idx_zh_char_words_char ON zh_char_words(char);
CREATE INDEX idx_zh_char_words_word ON zh_char_words(word_id);
CREATE INDEX idx_notes_ko ON notes(ko_word_id);
CREATE INDEX idx_notes_zh ON notes(zh_word_id);
CREATE INDEX idx_char_variants_char ON char_variants(char);
```
