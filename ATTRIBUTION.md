# 원 저작물과 저작자 표시 (Attribution)

이 자료는 아래 저작물을 바탕으로 만들었습니다. 쓰실 때 이 목록의 저작자를 밝혀 주세요.
전체 자료는 **CC BY-SA 4.0** 으로 공개합니다([LICENSE](LICENSE)). 아래 표의 라이선스는 각 원 저작물 자체의 것입니다.

> 권장 표시: 「국립국어원 표준국어대사전·한국어기초사전, CC-CEDICT, Unicode Unihan 을 바탕으로 한 한중종합사전 사전 데이터 (CC BY-SA 4.0)」

## 한눈에

| 원 저작물 | 저작자 | 원 라이선스 | 이 자료의 어디 |
|---|---|---|---|
| 표준국어대사전 | 국립국어원 | CC BY-SA 2.0 KR | `ko_words` `ko_senses` `ko_synonyms` |
| 한국어기초사전 | 국립국어원 | CC BY-SA 2.0 KR | `ko_words.level` `ko_zh_equivs` |
| CC-CEDICT | MDBG 와 CC-CEDICT 기여자들 (CEDICT © 1997, 1998 Paul Andrew Denisowski) | CC BY-SA 4.0 | `zh_words` `zh_senses.en` `zh_char_words` `char_variants`(cedict) |
| Unihan Database | Unicode, Inc. | Unicode License v3 | `glyphs` `char_variants`(unihan) |
| CC-CEDICT 한국어 풀이 | AI 번역 (이 자료의 2차 저작물) | CC BY-SA 4.0 | `zh_senses.ko` |
| 한·중 비교 해설·예문 | AI 집필 (이 자료) | CC BY-SA 4.0 | `notes` |

## 표준국어대사전

- 저작자: 국립국어원 — https://stdict.korean.go.kr/
- 라이선스: 크리에이티브 커먼즈 저작자표시-동일조건변경허락 2.0 대한민국 (CC BY-SA 2.0 KR) — https://creativecommons.org/licenses/by-sa/2.0/kr/
- 저작권 정책: https://stdict.korean.go.kr/join/copyrightPolicy.do
- 가져온 것: 원어 한자가 있는 낱말(한자어·혼종어) 전부의 표제·뜻풀이·품사·발음·어종, 그리고 한자·중국어로 이어지는 고유어의 표제·뜻풀이, 뜻에 달린 동의어·비슷한말.
- 우리가 바꾼 것: 표를 나누어 담았고(`ko_words` `ko_senses` `ko_synonyms`), 동음이의 번호를 표제와 떼어 두었고, 낱말 번호(`id`)와 정렬값(`rank`)을 붙였습니다. 고유어는 같은 뜻 한자어나 중국어 대응어로 이어지는 것만 골랐습니다.

## 한국어기초사전

- 저작자: 국립국어원 — https://krdict.korean.go.kr/
- 라이선스: CC BY-SA 2.0 KR — https://creativecommons.org/licenses/by-sa/2.0/kr/
- 저작권 정책: https://krdict.korean.go.kr/kboardPolicy/copyRightTermsInfo
- 가져온 것: 기초 어휘 등급(`ko_words.level`)과 뜻풀이마다 달린 중국어 대응어(`ko_zh_equivs`).
- 우리가 바꾼 것: 쉼표로 이어진 대응어를 후보 하나씩 나누었고, 표준국어대사전 낱말과 표제·원어(고유어는 표제·품사)로 맞춘 것만 담았으며, 같은 간체 표제의 CC-CEDICT 낱말이 있으면 `zh_word_id` 로 이었습니다.

> 라이선스에 대하여: 위 두 원 저작물은 CC BY-SA 2.0 KR 입니다. 이 자료는 전체를 CC BY-SA 4.0 으로 공개하며, 두 사전에서 온 부분에는 원 라이선스의 저작자표시·동일조건 의무도 그대로 지킵니다.

## CC-CEDICT

- 저작자: MDBG 와 CC-CEDICT 기여자들. CEDICT © 1997, 1998 Paul Andrew Denisowski — https://cc-cedict.org/wiki/
- 라이선스: CC BY-SA 4.0 — https://creativecommons.org/licenses/by-sa/4.0/
- 가져온 것: 표제(간체·번체)·병음·영어 풀이 전체, 그리고 한 글자 표제의 'variant of' 관계.
- 우리가 바꾼 것: 병음에 성조 부호를 붙인 `pinyin` 열을 더했고(`pinyin_num` 이 CC-CEDICT 원문), 낱말 번호·`rank`·HSK 3.0 등급 값(`hsk`)을 붙였고, 글자별 역색인을 만들었고, 이체 관계를 `char_variants`(source=cedict)에 양방향으로 담았습니다.

## CC-CEDICT 한국어 풀이 (`zh_senses.ko`)

CC-CEDICT 의 영어 풀이를 AI(OpenAI GPT 계열)로 한국어로 옮긴 것으로, CC-CEDICT 의 2차 저작물이라 CC BY-SA 4.0 입니다.
사람이 검수하기 전이라 틀린 곳이 있을 수 있어 영어 원문(`zh_senses.en`)을 나란히 둡니다.

## Unicode Unihan Database

- 저작자: Unicode, Inc. — https://www.unicode.org/charts/unihan.html
- 라이선스: Unicode License v3 — https://www.unicode.org/license.txt (전문은 이 문서 끝)
- 가져온 것: `kHangul` `kMandarin` `kDefinition` `kTotalStrokes` `kRSUnicode`(`glyphs`), `kSimplifiedVariant` `kTraditionalVariant` `kSemanticVariant` `kSpecializedSemanticVariant` `kZVariant`(`char_variants`).
- 우리가 바꾼 것: 필요한 필드만 골라 표로 옮겼고, 부수 번호를 강희부수 글자로 바꾸었으며(NFKD 로 통일 한자), 변이 관계를 양방향으로 두고 한국어 이름(간체·번체·이체자·일부 뜻 이체·자형 차이)을 붙였습니다.

## HSK 3.0 등급

`zh_words.hsk` 는 중국 교육부 「国际中文教育中文水平等级标准」(GF0025-2021)의 단어 등급을 낱말에 붙인 값입니다. 등급 값만 쓰고 표준 문서의 단어표 자체는 싣지 않았습니다.
이 값은 원 문서에서 온 사실 정보이며, 이 라이선스가 그에 대한 권리를 새로 만들어 주지는 않습니다.

## 이 자료가 더한 것

- 한·중 비교 해설과 예문 985건(`notes`): AI 가 썼고, CC BY-SA 4.0 으로 함께 공개합니다. 사람이 검수하기 전입니다.
- 같은 한자 표기의 한·중 연결(`ko_zh_links`), 글자 → 낱말 역색인(`ko_char_words` `zh_char_words`), 정렬값(`rank`).

## 이 자료에 넣지 않은 것

- 한국어문회 배정한자 자료(훈음·급수 등). 별도의 권리가 있어 앱 안에서만 쓰며 이 공개본에 넣지 않았습니다.
- 앱의 중국어 발음 녹음(VoxCPM2 로 합성). 이번 공개에 넣지 않았습니다.
- 앱 소스 코드와 화면 글꼴.

---

## Unicode License v3 (전문)

Unihan 에서 온 데이터(`glyphs`, `char_variants` 의 source=unihan 행)에 대한 고지입니다. 출처: https://www.unicode.org/license.txt

```text
UNICODE LICENSE V3

COPYRIGHT AND PERMISSION NOTICE

Copyright © 1991-2026 Unicode, Inc.

NOTICE TO USER: Carefully read the following legal agreement. BY
DOWNLOADING, INSTALLING, COPYING OR OTHERWISE USING DATA FILES, AND/OR
SOFTWARE, YOU UNEQUIVOCALLY ACCEPT, AND AGREE TO BE BOUND BY, ALL OF THE
TERMS AND CONDITIONS OF THIS AGREEMENT. IF YOU DO NOT AGREE, DO NOT
DOWNLOAD, INSTALL, COPY, DISTRIBUTE OR USE THE DATA FILES OR SOFTWARE.

Permission is hereby granted, free of charge, to any person obtaining a
copy of data files and any associated documentation (the "Data Files") or
software and any associated documentation (the "Software") to deal in the
Data Files or Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, and/or sell
copies of the Data Files or Software, and to permit persons to whom the
Data Files or Software are furnished to do so, provided that either (a)
this copyright and permission notice appear with all copies of the Data
Files or Software, or (b) this copyright and permission notice appear in
associated Documentation.

THE DATA FILES AND SOFTWARE ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT OF
THIRD PARTY RIGHTS.

IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED IN THIS NOTICE
BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT OR CONSEQUENTIAL DAMAGES,
OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THE DATA
FILES OR SOFTWARE.

Except as contained in this notice, the name of a copyright holder shall
not be used in advertising or otherwise to promote the sale, use or other
dealings in these Data Files or Software without prior written
authorization of the copyright holder.
```
