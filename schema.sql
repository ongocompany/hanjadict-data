-- hanjadict-data 공개 SQLite 스키마 (export_public.py 가 만든다)

CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE ko_words (
  id INTEGER PRIMARY KEY,
  headword TEXT NOT NULL,
  homonym_no INTEGER,
  hanja TEXT NOT NULL,
  word_type TEXT,
  pos TEXT,
  pronunciation TEXT,
  is_affix INTEGER NOT NULL DEFAULT 0,
  level INTEGER,
  rank INTEGER NOT NULL
);
CREATE TABLE ko_senses (
  word_id INTEGER NOT NULL,
  sense_no INTEGER,
  definition TEXT NOT NULL,
  category TEXT
);
CREATE TABLE ko_zh_equivs (
  word_id INTEGER NOT NULL,
  ord INTEGER NOT NULL,
  ko_definition TEXT NOT NULL,
  zh TEXT NOT NULL,
  zh_word_id INTEGER
);
CREATE TABLE ko_synonyms (
  word_id INTEGER NOT NULL,
  syn_id INTEGER NOT NULL,
  kind TEXT NOT NULL,
  ord INTEGER NOT NULL,
  PRIMARY KEY (word_id, syn_id)
);
CREATE TABLE zh_words (
  id INTEGER PRIMARY KEY,
  simplified TEXT NOT NULL,
  traditional TEXT NOT NULL,
  pinyin TEXT NOT NULL,
  pinyin_num TEXT NOT NULL,
  hsk INTEGER,
  rank INTEGER NOT NULL
);
CREATE TABLE zh_senses (
  word_id INTEGER NOT NULL,
  ord INTEGER NOT NULL,
  ko TEXT,
  en TEXT NOT NULL
);
CREATE TABLE ko_zh_links (
  ko_word_id INTEGER NOT NULL,
  zh_word_id INTEGER NOT NULL,
  PRIMARY KEY (ko_word_id, zh_word_id)
);
CREATE TABLE ko_char_words (
  char TEXT NOT NULL,
  word_id INTEGER NOT NULL
);
CREATE TABLE zh_char_words (
  char TEXT NOT NULL,
  word_id INTEGER NOT NULL
);
CREATE TABLE notes (
  ko_word_id INTEGER,
  zh_word_id INTEGER,
  pilot_id TEXT NOT NULL,
  relation TEXT NOT NULL,
  comparison TEXT NOT NULL,
  zh_definition TEXT NOT NULL,
  examples TEXT NOT NULL
);
CREATE TABLE glyphs (
  char TEXT PRIMARY KEY,
  reading TEXT,
  pinyin TEXT,
  en_def TEXT,
  stroke_count INTEGER,
  radical TEXT
);
CREATE TABLE char_variants (
  char TEXT NOT NULL,
  variant TEXT NOT NULL,
  kind TEXT NOT NULL,
  source TEXT NOT NULL,
  PRIMARY KEY (char, variant, kind)
);
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
