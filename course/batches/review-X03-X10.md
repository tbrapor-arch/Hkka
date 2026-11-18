# Review of 外篇 3–10 (files 73–80, app ids 173–180), 18 Nov 2026

Fresh agent, working alone against `data/build/hakka.db` after `make lint` showed 0 errors. Every new word's reading was
checked against kaga115, kaga and MOE (all 268 declared readings come from one of them); every polyphonic character
and every `check: true` line was read in context, and the patterns searched in the `example` table. Counts are
official Sixian sentences (kaga115 + kaga) / MOE examples, as the counting rule asks.

Severity: **CERTAIN** = the data proves it wrong. **LIKELY** = the data points against it. **DOUBT** = cannot be
attested either way; the question for a native speaker is given. The last column says what was done (branch
`review-extra-stories`).

## Summary

| Story | CERTAIN | LIKELY | DOUBT | Reliability |
|---|---|---|---|---|
| 外篇 3 (73) | 1 | 1 | 2 | good: 11 official lines, the course's lines are plain |
| 外篇 4 (74) | 1 | 1 | 1 | good: half the lines official, the rest close to official sentences |
| 外篇 5 (75) | 1 | 1 | 0 | good |
| 外篇 6 (76) | 0 | 1 | 2 | fair: many course lines, but each follows an official pattern |
| 外篇 7 (77) | 1 | 1 | 1 | fair |
| 外篇 8 (78) | 0 | 3 | 2 | fair: the letter frame has the most calques (好香, 轉來 "then", 𠊎个間房) |
| 外篇 9 (79) | 1 | 2 | 4 | weakest: the speech's own lines are the least attested (𫣆兜, 有落著, 知麼个係麼个) |
| 外篇 10 (80) | 1 | 0 | 2 | fair: 29 course lines, but their patterns are attested (尋人出水, 無奈何, 毋贏, 還合) |
| **Total** | **6** | **10** | **14** | |

The five worst problems:
1. 喊 read ham "tell to" where it means "shout, call out" (外篇 5 line 28 緊喊救命, 外篇 7 line 9 緊尋緊喊): MOE
   緊喊 ginˋ hemˊ "一直叫喊"; the card already lists 緊喊 (hemˊ). New rule `shout-hem`.
2. 外篇 9 line 19: 阿舅 says "last year nothing he did came off; this year his luck has turned, everything goes
   well" right after "the first month went badly", about 阿傑 whose 2029 stall did well (進修 61, 63).
3. 外篇 8: 轉來 used for "then" (line 8), 好香 "smells so good" (line 13, 0 official; kaga 當香), 𠊎个間房 (lines
   29–30, 0 official; kaga115 厥間房, MOE 若間房, card).
4. 外篇 4 note 0 says Grandpa was "born in 1949, lesson 65": lesson 65 gives no age.
5. Sentence-final 哩 in three course lines (外篇 3, 5, 9): no other 進修 line of the course's own has it; the course
   writes 吔. New rule `final-li`.

Doubts the writer listed in `P74.md` that the data settles:
- 上下 "about" (外篇 6 line 13): kaga115 itself glosses 上下 "經過；左右，約略之意" and gives 這尾石斑仔，差毋多有兩斤上下.
  The note now cites it.
- 開洋 (外篇 9 line 11): the kaga115 gloss is general, "形容陽光及視界良好的地方"; only the example is a grave site. Fine.
- 見 "every time" (外篇 7 line 16): four kaga115 sentences translate 見看(著)人 as 每次看到 / 每每. Fine.
- 發 bodˋ (外篇 4 line 17): kaga and kaga115 read 發 bodˋ in some 25 ailment words (發瘡仔, 發痔仔, 發疔仔, 發癬, 發痧). Fine.
- 毋使用著 (外篇 4 line 25): both official sentences gloss 用著 as 用到 (a result): doˋ, as the card's V著 rule. Fine.
- 歷史 lag saiˋ (外篇 5 line 33): kaga115 entry 底細（閩南語借詞）, and the line is its own example. Fine.
- 無結煞 (外篇 7 line 26): 16 official sentences use it; the reading moˇ gadˋ sadˋ is MOE's (no list entry). Fine.
- 由在 iuˇ cai (外篇 10 line 34): MOE entry 由在 iuˇcai and the MOE saying. Fine.
- 有求必應 (外篇 3 line 26): a kaga115 sentence; 應 in as in MOE 答應 dabˋin. Fine.
- 菜弇仔弇等 (外篇 3 line 6): kaga115 entry 弇 kiemˇ 罩子 has this example; the verb 弇 giemˇ is the other kaga115 entry. Fine.
- 當在該 dongˊ di ge (外篇 3 line 5): the kaga115 entry 當在該… reads di ge (the card's du ge is MOE's 在該 alone). Fine.

## 外篇 3 (73)

| Line | Finding | Evidence | Severity | Done |
|---|---|---|---|---|
| ex. translate 3 | 阿姆逐日七早八早就䟘起來運動 is a kaga sentence quoted with no `source:` | `example` (kaga): 阿姆逐日七早八早就䟘起來運動。; 322 of 400 translate items in 進修 carry `source:` | CERTAIN | fixed: `source: kaga`, `abridged: true` (the kaga sentence ends 運動(做事)) |
| 17 | 割禾哩: sentence-final 哩 in the course's own line | checklist (recounted): the course writes 吔 leˊ; no other own line of 進修 1–70 has 哩 | LIKELY | fixed: 割禾吔; rule `final-li` |
| 28 | 說人 for "talk about people behind their backs" (gossip) | kaga115 說人 "稱說（稱讚人）" (praise); only kaga 2013 says "批評人或稱讚人". The one sentence is the saying 誰人背後無人說，哪個人前不說人 | DOUBT | left, `check: true`. Ask: can 背後說人 mean "speak ill of people behind their backs"? |
| 11 | 讀書讀到變扁身 "studying has made me skinny" | 扁身 kaga115 "身體及臀部扁而瘦的體型" is a build, no sentence; "become 扁身" unattested | DOUBT | left, `check: true`. Ask: can one "become" 扁身 by losing weight? |

## 外篇 4 (74)

| Line | Finding | Evidence | Severity | Done |
|---|---|---|---|---|
| note 0 | "he was born in 1949, lesson 65": lesson 65 gives no age or year | lesson 65 has no 歲 or year for Grandpa; lesson 40 (winter 2026), Grandpa: 𠊎七十八歲 | CERTAIN | fixed: "seventy-eight in lesson 40 (winter 2026), so born in the late 1940s" |
| note 22 | "the list also gives gienˊ nai" | kaga115 堅耐 gienˊ ngai only; gienˊ nai is kaga 2013 (gienˊngai gienˊnai) | LIKELY | fixed: "kaga (2013) also gives" |
| 8 | 有兜送去分火車燒 "went to feed the trains" | 送去分 + V: 0 / 0 | DOUBT | left, `check: true`. Ask: natural for "some was sent to be burnt by the trains"? |

## 外篇 5 (75)

| Line | Finding | Evidence | Severity | Done |
|---|---|---|---|---|
| 28 | 緊喊救命 read ham; shouting is hemˊ | MOE 緊喊 ginˋhemˊ "一直叫喊"; 喊 hemˊ "大聲叫喚"; card: 喊 ham "tell someone to", hemˊ "shout"; "check 緊喊 (hemˊ) every time" | CERTAIN | fixed: hemˊ; rule `shout-hem` |
| 30 | 佢青瞑哩: final 哩 in an own line | as 外篇 3 line 17 | LIKELY | fixed: 吔 |

Checked and right: 合共下 (kaga115 阿明輒常同不褡不膝个朋友合共下), 在田項勞碌 (kaga 歸隻熱天都在田項勞碌), 冤家泌背 of a
village (kaga115 舞到歸莊人冤家泌背), 佢這人-type 阿貴這人 (9 kaga115 with 這人), the title (MOE entry 日仔吂到，毋係天公毋報).

## 外篇 6 (76)

| Line | Finding | Evidence | Severity | Done |
|---|---|---|---|---|
| 35 | "yesterday afternoon, when the rain stopped, children played in the mud": the only rain told is the typhoon at dinner time and all night (lines 2–3), so the mud and the pause belong to this morning | internal: lines 2, 3, 30 | LIKELY | fixed: 今晡日朝晨 "this morning" |
| 24, 27 | 拚路 "clear the road" | 拚路 0 / 0; 拚 "清理" is an MOE sense; kaga115 has 阿爸摎路頭路尾个樹椏仔拈開 for clearing branches | DOUBT | left, `check: true`. Ask: is 拚路 said for clearing a road after a storm? |
| 12 | 山項有一隻莊頭推山 "a landslide at a village" | 推山 one sentence (地動最驚推山埋人个災害), subject a hill | DOUBT | left, `check: true`. Ask: can a village be the subject of 推山? |
| note 13 | (writer's doubt) 上下 "about" | kaga115 gloss 左右 and kaga115 例如：這尾石斑仔，差毋多有兩斤上下 | — | note now cites kaga115 |

## 外篇 7 (77)

| Line | Finding | Evidence | Severity | Done |
|---|---|---|---|---|
| 9 | 緊尋緊喊 "searched and called out", 喊 read ham | as 外篇 5 line 28 (MOE 緊喊 ginˋhemˊ) | CERTAIN | fixed: hemˊ |
| 12 | 問阿湖喊麼个名 "asked his name" | 喊麼个名 0 / 0; 安到麼个名 2 official (kaga115 若倈仔安到麼个名？); card: "What is X called" is X 安到麼个名 | LIKELY | fixed: 安到麼个名 |
| 21 | 阿姆同阿伯同該後生人頷頭: two 同 in a row (with / to) | no official sentence with 同 X 同 Y + verb | DOUBT | left, `check: true`. Ask: is 同阿伯同該後生人頷頭 clear, or 同阿伯摎該後生人? |

Checked and right: 行開一下仔定定 (kaga115 阿英行開一下仔定定), 睡忒 "fall asleep" (5 official), 該後生人 (kaga115),
the title (kaga 爺娘惜子長江水，子想爺娘擔竿長).

## 外篇 8 (78)

| Line | Finding | Evidence | Severity | Done |
|---|---|---|---|---|
| 8 | 轉來，阿婆教𠊎煎魚 "Then Grandma taught me": 轉來 is "come back" | the 10 official sentences with 轉來， all mean "come back" (佢對德國轉來，…); "next" is 續下來 (外篇 6; kaga115 佢講煞，續下來換你) | LIKELY | fixed: 續下來 |
| 13 | 就講好香 "said it smelt so good" | exclamative 好香 0 official; 當香 (kaga 該間店仔賣个仙貝當香), 盡香 (2 kaga) | LIKELY | fixed: 當香 |
| 29, 30 | 𠊎个間房 "my room" | 𠊎个間房 0 / 0; kaga115 厥間房整理到當揫亼; MOE 若間房; card: 你个/𠊎个 + home is 若間房 (batch 9) | LIKELY | fixed: 吾間房 (also in 進修 46, outside this review: left) |
| 29 | 盡好人去看佢 "loves to have visitors": 好 hau + a clause | 好人去 0 / 0; 好 hau is followed by a verb in the data | DOUBT | left, `check: true`. Ask: is 盡好人去看佢 natural? |
| 33 | kaga 老妹个皮膚白淨白淨 in 叔婆's mouth for "your sister" | the kaga sentence is about one's own sister; 若老妹 would be "your sister" | DOUBT | left (official sentence). Ask: can 叔婆 say 老妹 of Sam's sister? |

## 外篇 9 (79)

| Line | Finding | Evidence | Severity | Done |
|---|---|---|---|---|
| ex. translate 5 | 你先行，𠊎後背跈等來 is the second half of a kaga115 example, quoted with no `source:` | `example` (kaga115): 囥（庰）在門後背。你先行，𠊎後背跈等來。 | CERTAIN | fixed: `source: kaga115`, `abridged: true` |
| 19 | 阿舅: "last year nothing he did came off; this year his luck has turned, everything goes well", after "the first month went badly"; 阿傑's 2029 went well (進修 61 business picking up, 進修 63) | internal and state.md | LIKELY | fixed: the kaga115 sentence 你這毋成腳士，愛做麼个大頭路？ (Uncle teasing; 毋成 kept) |
| 35 | 𠊎就麻煩哩: final 哩 in an own line | as 外篇 3 line 17 | LIKELY | fixed: 吔 |
| 14, 22, 23, 33 | 𫣆兜 (inclusive) in a speech to staff, friends and 阿舅 about "our shop" | card: 阿傑 says 𠊎兜 to people outside the business; here part of the audience is the staff | DOUBT | left, `check: true`. Ask: with staff and guests listening, 𫣆兜 or 𠊎兜? |
| 27 | 普普仔知麼个係麼个 "know roughly what's what" | 知麼个係麼个 0 / 0 | DOUBT | left, `check: true`. Ask: idiomatic? |
| 27–28 | 阿舅講𠊎學法國話：教佢恁多擺… "you've taught him so many times": 阿舅 does not teach French | internal | DOUBT | left. Ask: can the quote be read as 阿舅 speaking for the teacher? |
| 32 | 有落著 "has found its feet" | 落著 only in 無落著 (kaga115 到今還無落著); 有落著 0 / 0 | DOUBT | left, `check: true`. Ask: is 有落著 said? |

Checked and right: 生理做毋成 (MOE 你个生理乜做毋成), 有好打幫 (kaga115 厥屋下食水果多多少少有好打幫), 無幾遠, 開洋
(see summary), 做毋著 mˇ cog in line 30 (official gloss 犯錯), the title (MOE entry 條條馬膦臭汗臊，百般頭路百般難).

## 外篇 10 (80)

| Line | Finding | Evidence | Severity | Done |
|---|---|---|---|---|
| 31 | English "and keep changing" for 三不二時就改變 | 三不二時 kaga115 "偶而、有時候" "now and then" | CERTAIN | fixed: "and every so often they change" |
| 33 | 你想愛分人人都歡喜 "please everyone": 分 + person + 歡喜 | 0 / 0 | DOUBT | left, `check: true`. Ask: natural for "make everyone happy"? |
| 18 | 兩儕人一抹煞騎在牛背項: 一抹煞 "all" of two riders | 一抹煞 in 4 official sentences, always things or matters (這一抹煞分你) | DOUBT | left, `check: true`. Ask: can 一抹煞 gather two people? |

Checked and right: 無奈何 (7 official), 尋人出水 (kaga115 滿哪尋人出水), 㧡毋贏 (V毋贏 13 official), 還合 (3 kaga115),
天理 (kaga 還無天理哪), 無人親像 (kaga115), the title (MOE entry 一張嘴兩層皮，講好講壞由在佢).

## Rules and card lines added
- `rules.yaml`: `shout-hem` (緊喊 / 喊救命 read ham), `final-li` (sentence-final 哩 in an own line). Evidence in
  `checklist.md`, "外篇 3–10 review".
- `card.md`, one line: 轉來 is "come back", never "then" (續下來, 後來 "later"); "smells good" is 當香 / 盡香, not 好香.
- `final-li` also flagged four fill items of 進修 39, 47, 57 and 64: each is an official kaga115 sentence with its own
  哩, so they carry `ok: [final-li]`. `make lint`: 0 errors, the same 182 warnings as before (the ones P74.md explains).
