# Writing checklist (from the reviews of batches 1–14)

Read before writing a batch. Each point is something a reviewer caught in a draft, with the evidence it rests on
(official example sentences in `example`, Glossika, the MOE dictionary).

## Counting rule (read first)
- The `example` table mixes three pools: **kaga115 + kaga, the official lists**, with an accent on every sentence
  (Sixian 14,969 sentences, Hailu 15,123), and **20,185 MOE dictionary examples with no accent** (and no pinyin).
  Earlier counts labelled "Sixian" added the MOE pool to the official Sixian one, and MOE examples often carry the
  other accent's word in brackets (韶早﹝天光日﹞).
- So: any claim of the form "Sixian says X, Hailu says Y", "X is commoner", or "N examples" counts the official lists
  only, per accent (`source in ('kaga','kaga115') and accent=?`). MOE hits are reported separately as "accent
  unmarked". In SQL: `select count(distinct hanzi) from example where source in ('kaga','kaga115') and accent='sixian' and hanzi like '%X%'`.
- Rules below that rested on mixed counts have been corrected in place (marked *recounted*).

## Before writing a line
- Search the pattern, not only the words: `hw.py ex 片段`, `hw.py gl 片段`. A line whose pattern has no attestation
  either changes or gets `check: true` and a note saying so.
- Prefer an official example sentence word for word when it fits the scene (`source: kaga115`): it has a recording.

## Readings and words
- 在 "be at" is coiˊ (Hailu coiˋ) in speech; cai is literary. 在該 + verb is du ge (Hailu diˇ gai).
- "What time" is 幾多點, not 幾點; "what number" 幾多號.
- 點鐘 is mostly a duration and takes 久: 兩點鐘久.
- Hailu "thank you" is 承蒙你 (with an object).
- 喊 "tell (someone) to" is ham; hemˊ is "shout, call out".
- Bus stop 車牌, station 火車頭 / 車頭; chilli 辣椒仔 (粒).
- 寒 for feeling cold (Hailu 冷); 冷 for cold things.
- Hailu 小 is siauˊ (shauˊ is 少).

## Grammar
- "We": 𠊎兜 excludes the listener, 𫣆兜 includes. Check every 𠊎兜 against who is listening.
- Adjectives are negated with 毋會 / 無 (毋會辣, 毋會貴, 無甜), not bare 毋.
- "Talk to someone" is 同 X 講話; 同 X 講 is "tell X".
- A demonstrative before a noun takes a classifier: 該隻阿伯, 這領衫.
- 盡 is "very" as often as "most"; say so whenever it appears.
- "I told you" is 𠊎講過吔 / 𠊎就同你講過吔, not *𠊎講吔.
- "How do you know?" is 你仰會知？; 仰般 is "how / how is it".
- 你先行 is the attested "after you"; 你行先 is described but unattested.
- 較 X 兜仔 "a bit more X" (with 仔).
- *Recounted:* sentence-final 了 is almost absent from the official lists (3 Sixian, 3 Hailu); the 759 were MOE.
  The official sentences end a change of state with Sixian 吔 (356) or 哩 leˊ (211, a kaga entry), Hailu 咧 leˋ (715).
  Decided (final pass): the course writes 吔 leˊ in Sixian and 咧 leˋ in Hailu, as the lists do; MOE quotations keep
  their 了 (lesson 2 note).

## People
- Sam calls Mrs Liu 伯姆, not 阿姆; the family says 阿姆.
- Grandpa's lines are few; keep counts in notes honest.

## Notes
- No "never" or "always" without evidence; no unverified geography or history (pottery in 公館, "no buses").
- Check note references against line numbers after any insertion.
- Check continuity: day of the week, who is home, what was eaten when.

## Added after the batch 4 review
- Sam is French (surname Martin), as in Tsheh-tû; Lucie speaks French only, her lines stay in French.
- 好 hau + verb = "like doing" (好食 "greedy"); "tasty" is 好食 hoˋ siid. Don't write 盡好食 for "loved it".
- "Tonight" is 今暗晡; plain 暗晡 is "evening".
- Demonstrative + classifier + noun, always (這隻外國人).
- 做毋得: three syllables in the example sentences (zo mˇ dedˋ); zomˇ dedˋ is the dictionary contraction.
- 係毋係 is he mˇ he (three syllables).
- Ill = 破病 (病 is the noun); unwell = 毋鬆爽; smoke = 食菸.
- 死 + adjective: only 死鹹 is attested; don't generalise.
- 三腳採茶: one clown and two girls. Temple opera: ritual in the morning, plays in the afternoon.
- Every new word should appear in the dialogue if at all possible, not only in exercises.
- Count Grandpa's lines before writing a note about how little he says.

## Added after the batch 5 review
- Hailu rain is 落水 (official: Sixian 落雨 70 / 落水 6, Hailu 0 / 73); Hailu 聽講 is tangˇ gongˊ; Hailu V等 is denˊ
  (43 of 47 Hailu V等 list words; nenˊ a variant, the usual Glossika form); Hailu 飯 is pon+.
- "Bed" is 眠床 (床 alone is a classifier). "In the pocket" is 褲袋肚 / 衫袋肚.
- 跌在 (drop somewhere), not 跌忒在. "Shut the window" 窗門關好來 (關等 = kept shut).
- 寄到哪位, not 寄去. 借分 + person for "lend". 一封信仔, not 一張信.
- "Get on well" is 感情當好. "Finish eating" is 食飽 (食煞 unattested; 講煞 is fine).
- Sixian "winter" is 寒天 (Hailu 冷天): official 寒天 51 / 1, 冷天 0 / 47.
- Keep a calendar for each batch: weekday of each lesson, who is at school or work.
- 𫣆兜 + verb includes the listener: don't use it to leave a conversation with neighbours.

## Added after the batch 6 review
- An injection is 注射 (打針 is unattested).
- No bare 毋 + adjective, ever: 毋會嚴重, 毋會譴.
- 舊年 is always "last year"; "this year is nearly over" is 今年愛過忒吔.
- "Nice and fine" is 幼幼仔 (剁到幼幼仔), not 當幼. "Give it a stir" is 摝摝仔.
- "Never (have done)" is 毋識 + V過 (你毋識講過), not 無 V過.
- No claims about how long or short a character's lines are unless you have counted.
- Check a rhyme on the Sixian finals as well as the Hailu ones (時 siiˇ / 知 diˊ only rhymes in Hailu).
- 頭家 is the owner or boss, not the waiter (服務生).

## Added after the batch 7 review
- Demonstrative + classifier for every noun, including 帖: 這張帖仔 (or the attested 行帖分).
- 毋著 has two readings: mˇ cog "wrong, at fault" (係𠊎毋著); after a verb, mˇ doˋ "not manage to" (拿佢毋著, 做毋著
  "can't do it"). Don't use 做毋著 for "did wrong".
- 恁仔細 stands alone; give the reason in its own clause (感謝大家來！恁仔細！). Hailu 承蒙 can take the person.
- Quote official sentences exactly, character for character (斯會 is not 就會), and mark them `source: kaga115`.
- No claims about customs (weddings, red envelopes, households) without an example sentence; say "general
  knowledge" when that is the source.
- Check every "lesson N" in the notes by grep before committing.
- "Online" is 在網路, not 網路項; "within N days" is N日內.

## Added after the batch 8 review
- 𫣆兜 includes the listener. When the listener is outside the group (Grandma telling Sam what "we" do every year,
  竹東 relatives telling a Miaoli guest), say 𠊎兜.
- 恁大仔 / 恁多仔 are predicative only: 皮箱正恁大仔, never 恁大仔个皮箱.
- "The first time" is 頭一擺; 頭擺 is "formerly, in the old days".
- 尞天穿 "rest on 天穿日" is attested (天穿日愛尞天穿, 客人有尞天穿个風俗). Before writing "no example supports this
  custom", grep `example` for the custom's key words.
- A Hailu-only word (韶早) has no Sixian reading: put it in the Hailu line only and let the English say so.
- After 恁仔細 nothing follows (no 你兜, no object): see batch 7.

## Added after the batch 9 review
- 頭先 is "just now" (剛才); for "at first" prefer 一開始 (see batch 13: kaga also gives 最初).
- News items take 條 (下一條新聞, 有一條新聞講…), not 隻.
- A number + 零 still takes its classifier: 兩百零个人 (這間工廠請有兩百零個工人).
- Don't overstate or understate Sixian/Hailu differences: count per accent in the official lists (counting rule).
  *Recounted:* the batch 9 claim that 糜, 落水, 肚屎枵, 承蒙 and 所以 "occur in Sixian examples too" came from the MOE
  pool. In the official lists the differences are real: 粥 / 糜 Sixian 32 / 6, Hailu 0 / 40; 肚飢 / 肚屎枵 12 / 0 and
  0 / 9; 恁仔細 / 承蒙 4 / 1 and 0 / 5; 故所 / 所以 137 / 1 and 4 / 131; Sixian 落水 (6) means "fall into the water".
- Keep the internal timeline consistent across a batch: weather (when the rain starts and stops), dates of events
  reported later, drive times, where people live.
- A Latin-letter word in a line (fan, pon) is stripped from the pinyin at its first match: put it before any
  syllable spelled the same (pon+, fan) or lint misaligns the line.

## Added after the batch 10 review
- 還好 + adjective is "very" (還好食 "really tasty"), not the Mandarin "so-so". "Not bad" is 會做得 (生理會做得).
- Comparison: 比 + adjective + amount needs no 較 (比𠊎高一息仔, 比你高五公分); 比 + 較 + adjective without an amount.
- 高過 is not a comparative in the data; 贏過 is "have won (before)".
- Ranks take a verb: 得著頭名, 得著第三名 (also 打頭名).
- "I miss you" out loud is 盡想你; 想念 has no official sentence (one MOE example).
- 一開始 "at the start" (prefer it to 頭先, which is mainly "just now").
- Before writing "not in the data", check the MOE definitions too (五月雪 is in the 桐花 entry).
- Keep a story decision for the lesson the brief gives it (A-in's job: the interview in 75, so 68–70 only decide to go).

## Added after the batch 11 review
- Sam calls Mrs Liu 伯姆, never 阿姆 (阿姆 is "Mum", for A-in and A-min only).
- An official sentence often differs between accents (同 / 摎, 莫 / 毋好, 了 / none): quote each accent's own version.
- Southern Sixian (美濃, 六堆): use the 176 parallel sentences, `sentence.accent='south-sixian'`, before the brackets.
- "Young people" is 後生人 (official 54 / 56; 年輕人 none).
- Sentence-final 哦 is oˊ (MOE 勸誡 sense); 呢 neˇ and noˋ are free variants in Sixian.
- 姐婆 is the maternal grandmother (外婆), not Grandma's mother.
- Hailu also says 盡 for "very" (盡少 15 / 15, 最少 0 / 1); don't swap it for 最 in the Hailu column.

## Added after the batch 12 review
- 聞 vunˇ means "hear" (a book word); "smell" is 鼻 pi (你鼻看啊, 鼻得着滿屋个清香).
- "Do it wrong" is V毋對 (唱毋對, 七做八毋對); 毋著 after a verb means "not manage to".
- 毋會講話 means "mute, can't speak": don't use it for "I'm no good at talking".
- A song or verse quote needs its source (the dictionary's 引自…), never a copyright claim the data can't support.
- Gloss 盡 every time it appears ("very" or "most").
- An official sentence that exists only in Sixian: say in the note that the Hailu column is the course's transposition.

## Added after the batch 13 review
- Instrument verbs differ by accent: Sixian 鋸弦仔 / Hailu 挨弦仔 (official 2 / 0, 0 / 2); Sixian 吹笛仔 / Hailu 歕笛仔
  (one sentence each); 打鼓, 打銅鑼 (1 / 1) in both.
- "Get lost" is 撞走 (2026 list: 迷路), besides 尋毋著路. "Mist" is 濛紗煙 (Sixian) / 濛煙 (Hailu list); 濛紗煙恁重.
- Emergencies in the story call 119 and the 消防隊 comes; safety advice (walk slowly in the dark, ice a twisted ankle) follows an official sentence or is labelled general knowledge.
- 頭先: "just now" in kaga115, but kaga (2013) also gives 最初 "at first". Prefer 一開始 for "at first", and don't claim 頭先 is "always" one thing.
- Before claiming anything about a character's previous lines (longest, first, never), grep them.
- "Not in the data" claims: also search the MOE definitions (四縣 → 嘉應州, 原鄉 in kaga).

## Added after the batch 14 review
- `source:` names the table that actually holds the sentence: kaga115 (has recordings), kaga (2013), moe (dictionary
  examples, no recording) or sentence (客語百句). Run the check before committing: every `source:` line's Sixian hanzi
  must be in that table word for word; a shortened quote gets `abridged: true`. MOE examples are often Sixian only:
  say so when the Hailu column is the course's version.
- 明年 is Sixian too (MOE miangˇ ngienˇ; kaga115 examples), though not a Sixian list entry; 過忒年 means "next year" and
  also "after New Year", in both accents.
- 識 means "know (a person, a word)" and "ever (have done)"; "can, know how to" is 會. 毋識講客話 = "had never spoken".
- 師傅話: quote kaga115 where it has the saying (十二月甘蔗－兩頭甜; Hailu 三隻鼻空笐), kaga or MOE otherwise, and say
  which; only call a saying an entry if it is one.
- Hailu shares 盡 (盡重要 8 / 8, 最重要 1 / 1). Write it in both columns.
- ABAB (烏陰烏陰, 好勢好勢) and AABB (清清楚楚): lint now accepts AABB of a listed word.

## 進修 batch 1 review (P1–P7)
- 黏時 is "at once, immediately" (馬上、隨即、立刻), not "suddenly"; "suddenly" is 好恬恬 (kaga115) or 無提無防.
- 問題 takes 隻 or 個 (這隻問題, 這個問題), not 條.
- A rainbow faces away from the sun: in the evening it is in the east, in the morning in the west (東弓晴，西弓雨;
  kaga: 朝晨頭若係出天弓，大體就會落雨).
- "Live (somewhere)" is 歇 hed (歇在: 22 official sentences); 住 cu only in compounds (住址, 對毋住).
- Adverb after the verb, also with 加: 買加兜仔, 讀加兜仔書, 識加兜人 (not 加買, 多讀, 多識).
- "Good points" is not 好个所在 (a calque); "to this day" is 到今 (36), not 到今晡日 (0).
- Daytime is 日時頭 (lesson 79). Before writing "our own phrase", check whether a taught list word already covers it.
- 毋正常 → 無正常 (0 / 4). 毋好 "bad" is lexicalised (對身體毋好, 人毋好) and is the one exception to the bare-毋
  rule; for marks, the lists say 成績毋理想.
- Before declaring a word, look for the same hanzi under any reading in Part 1 and earlier 進修 lessons
  (`candidates.py` shows DECLARED): 揚蝶仔 (lesson 69) and 開始 (lesson 58) were declared twice. Lint misses
  compounds used before their declaration (聽講): grep for them.
- Numbered items inside a text (leaflets, rules, news items) must run in order.
- In a review lesson, check the batch calendar before "long time no see" and similar lines.
- A new word's gloss must match a sense the list gives (kaga115 弓 is the classifier for a hand of bananas).

## 進修 batches 2–3 review (P8–P21)
- Demonstrative + bare noun: the classifier is the default. A bare noun only where an official sentence has one
  (這手鈪, 這茶, 這湯: one each); 這柚仔 has none → 這隻柚仔 / 這兜柚仔.
- 歇 for guests, guesthouses and visits is hiedˋ (短住、住宿; 你來歇兩暗晡); hed is "live" (長住). Check every 歇 in a
  guest scene.
- Names: X 安到 Y (lesson 22; 佢安到阿明). 名喊 is unattested.
- "Girlfriend" is 女朋友 (lesson 32; 8 official); 細妹條仔 is "lass" (少女). 交朋友 is friendship, not dating
  (交往 has no list reading). Matchmaking is 牽線 (MOE) or 做媒人 (3); 牽成 is a mentor's or boss's support (提攜).
- Number + 過 takes its classifier, like number + 零: 十過個, 萬過斤, 兩千過个人.
- "Never (in my life)": 從來毋識 + verb (6 official); bare 從來毋 + verb has none.
- 共下 is "together"; "in all" is 總共.
- 合 "match (horoscopes)" is hab (MOE 相匹配, 合婚; lesson 44); gab is only in 上合合.
- 無值 is unattested; "not worth it" is 毋值 (實在毋值, 4).
- Before calling a sentence "official", check its pool: a sentence with no accent is an MOE example (合過八字…).
- A review lesson reuses at least three new words from each of the six lessons before it. Count each lesson's
  `new_words` in the review dialogue.
- An official sentence that lint cannot read (禮 alone in 正有禮) is adapted with `check: true` and a note, not
  quoted with `source:`.

## 進修 batches 4–5 review (P22–P35)
- 逐 "every" is dagˋ (逐日, 逐禮拜, 逐項); giugˋ is "chase" (逐老鼠, 逐黃蚻). Seven "every" lines in P26–P33 had giugˋ:
  grep the pinyin of every 逐.
- 熟 "cooked, done" is sug (lesson 29); xiugˋ is "ripe" (kaga115: 指蔬果熟成). Check polyphonic words by sense, not
  only by lint: lint accepts any listed reading.
- 好 is hau before a verb also after 恁: 莫恁好逞強 "don't be so keen to act tough".
- 愛多 + verb for advice is attested (19 official: 愛多運動, 愛多溫習, 愛多尞), so the batch 1 rule against 多讀 is about
  quantity. With a number, the verb comes first with 加: 歇加兩暗晡 (official 歇加幾夜仔), not 多歇兩暗晡.
- "Not many" after a verb is V無幾多 (做無幾多, 賺無幾多錢), not V毋多.
- 睡忒晝 is "oversleep" (MOE); 晝 zu is "late" (忒晝吔！會赴毋著哩). "Go to bed late" has no example.
- In a letter, writer + reader is 𫣆兜 (𫣆兜兩儕當多話題好講); the writer's household welcoming the reader is 𠊎兜.
- Lint checks `source:` only in the dialogue, and not the table name. Check exercise sources by hand: 年初二轉妹家 is
  kaga115, not kaga; 得著好空 is half of 得著亞軍。得著好空 (`abridged: true`).
- A note quoting an official sentence keeps its own particles and adverbs (哩, 異), even where the course writes 吔
  and 當; a line or exercise that swaps them is the course's version and has no `source:`. 異 is not taught yet.
- A list entry whose only sense is a measure word (擔 量詞) is glossed from MOE for the verb (負責、承當), and the note
  says so.
- January–February: 今年, 舊年 and 天光年 differ by calendar until the lunar New Year. For seasons (longans, a
  harvest) name the season (熱天) instead of the year.
- Leaflets, rules, hours and limits of real Taiwanese institutions (the post office) are invented: say so in the
  setting.
- Continuity: Sam spent the winter of 2026–27 and the 2027 New Year with the Lius (Part 1, lessons 29 and 50–51): in Part 2
  it is not his "first winter" or "first New Year in Taiwan". 阿太 is Grandpa's father (lesson 65). Sam has a sister,
  Lucie (lesson 29). A-min has never met 鍾伯.
- 2029: the twelfth lunar month has 29 days, so New Year's Eve (Mon 12 Feb) is the 29th; it is still 年三十.

## Batch 6 (P36–P42), review of 10 Nov 2026
A fresh agent reviewed the seven lessons against the database after lint showed 0 errors. Counts are official Sixian
sentences / MOE examples. All findings below were fixed unless marked "left".
- **Readings the draft tool got wrong:** 共下 kiung haˊ → kiung ha (P42); 輪著 lunˇ → linˊ, as lesson 92 (lunˇ is an
  MOE-only reading, example 輪流) (P36); 無斯 moˇ siiˊ → moˇ siiˇ, the kaga115 entry (P41). Left: 斯 alone stays siiˊ,
  as lesson 65 teaches it, although MOE gives siiˇ for 斯 "就".
- **吾 as a subject**: 吾有一個老朋友 0 / 0; 吾 is always followed by a noun. → 𠊎有 (P40). 吾攤仔, 吾粄條 → 𠊎个 (P39).
- **年下** alone: MOE says 四縣不說「年下」; 4 official sentences have 年下仔. → 年下仔, now a new word of P39.
- **囥雨** 0 / 0 → 寄雨 gi iˋ (3 official), now a new word of P41.
- **差無幾多** 0 / 0 → 差毋多 (26 / 31) (P38). **這兜年** 0 / 0 → 這幾年 (2 / 8) (P38). **一袋仔 + noun** 0 / 0 → 一袋
  (3 official) (P37, P42). **細細間, 細細頭** 0 / 0 → 細細仔 (P39, P41). **名姓安到麼个** 0 / 0 → 佢安到麼个名 (P38).
- **English:** 同人打炭礦 is "dig coal for other people" (official gloss 替人家), not "with the other men" (P41).
- **Story:** P36 said "term started this week" on 27 Feb (it started on 19 Feb). P42 opened with "you haven't been for
  so long", eight days after the outing of P41. P41 went by car and "walked home". P42 had 叔婆 mend the trousers Sam
  mended himself in P37: now "last week".
- **Notes:** MOE gives 粄圓 as the Hailu word, not "the other accents"; 落 has three readings; a course line quoted in
  a note says which lesson it is from.
- Settled on 11 Nov 2026 for the whole course, from the MOE dictionary (the lists have neither word alone):
  斯 "then, so" is siiˇ in Sixian and sii+ in Hailu (siiˊ / siiˋ is only 斯文; kaga115 無斯 moˇ siiˇ agrees): 9 Sixian
  and 4 Hailu lines, the note, the exercise and the new word of lesson 65 corrected. 傑 is kied in Sixian and kiedˋ in
  Hailu: 阿傑 corrected in 17 Sixian and 6 Hailu lines. 瓦斯 keeps ngaˋ siiˊ (list reading).
  The synthetic audio of these lines in Hkka-private is now out of date: re-run `tools/tts.py` there.
- Checked and found right: every other reading of 著, 好, 落, 行, 下, 上, 會, 分, 正, 喊, 歇, 還, 倒, 降, 兩, 煞; the 229
  glosses; every sentence quoted in a note; all weekdays and lunar dates.

## Batch 7 (P43–P49), review of 11 Nov 2026
Fresh agent, read-only. 5 certain findings, all checked against the data before fixing; 3 of its "to check" points
were wrong and are not applied.
- 天穿日 "from 進修 36": it is taught in lesson 55 → fixed (P43 note).
- 釘: kaga115 gives dangˊ for both "nail" and "nail (verb)"; the lesson had dang and a note about another tone → fixed
  to dangˊ, note rewritten (P45).
- 無法度 "from lesson 60": it is in 進修 4 → fixed (P46 note).
- 共下 kiung haˊ in P48 line 1 (same slip as P42) → kiung ha; rule `together-tone` added and tested.
- 臺灣 toiˇ vanˊ in a P48 exercise → toiˇ vanˇ; card line added.
- P48: two fill items repeated lines of the text → new items. P49: all ten exercises copied lines of 43–48 → new
  sentences.
- Not applied: the 𫣆兜 quote in the P44 note is the kaga115 Sixian sentence (the agent read the kaga 2013 one); the
  P46 title is a kaga115 sentence; 撥 padˋ is the kaga115 reading (glossed 搧), so the gloss became "fan, flap".
- Lint warns "already used before it is taught" for 19 words of P43–P48 (過年過節, 法度, 手電筒 …): each was met
  earlier inside a line or an exercise and is now taught as a word. Accepted, as in batch 6.

## Batch 8 (P50–P56), review of 11 Nov 2026
Fresh agent, read-only. Each finding was checked in the data before fixing.
- Readings: 會 fi for "will" in a P50 exercise; 扣分 with bunˊ (P54, P56; kaga 扣分 kieu funˊ) → rule `marks-fun`;
  擇著 with cog (gloss 挑上 → doˋ); 背翕翕仔 built from single characters (list: boi him him eˋ) → the exercise was
  replaced; 事 "work" se in 輕可仔个事.
- 生个 is "alive" in the lists (活的), not "raw" → English and gloss fixed (P51).
- 膏藥仔 is a verb (敷藥); the noun is 膏藥 gauˊ iog (kaga115 example) → P52 line 30, word declared from MOE.
- 𠊎个肩頭, 𠊎頸根項 → 吾 (吾 + body part 14 official / 3 MOE; 𠊎个 + body part 0) → rule `my-body`.
- 重兩公斤 "weigh two kilos" → 重加兩公斤 (高加 4 official). 領錢 (bank) → 領工錢. 一隻攤仔 (0) → 擺攤仔 (3).
- 揉肩頭: 揉 is "crumple" in every example → 捶背囊 (2), 捶 declared; 揉 is not taught.
- Notes: 鬥雙 is from 進修 34, not 36; "Grandpa promised" in 進修 49 was Grandma's remark.
- Exercises repeating a line of the text: P51 (2), P55 (2), P56 (3 clauses) → new sentences.
- 鬥緊 was declared in P54 but first used in P50 (its title): now declared in P50.
- The factory makes 粄條 (lesson 53, 進修 39): 進修 45 and 49 said 麵 → fixed; card line added.
- 臺灣 was declared twice in Part 1 (lesson 52 with vanˊ, lesson 73 with vanˇ): lesson 52 now has toiˇ vanˇ and the
  second declaration is gone. This was the source of the wrong default in the draft tool.

## Batch 9 (P57–P63), review of 11 Nov 2026
Fresh agent, read-only. Findings checked in the data before fixing.
- The draft tool swallows a longer word: 大體會 read fi (體會; also in P43) → rule `will-voi`; 共下去 read haˊ in a
  quoted exercise (下去) → `together-tone` now also runs on quoted lines; 聽毋著, 拗著 with cog (→ doˋ; also in a P47
  exercise); 當好 + verb with hoˋ (→ hau); 緊喊 with ham (MOE ginˋ hemˊ); 正門 zang (kaga ziin munˇ).
- 冷淡 langˊ tam and 指教 ziiˋ gau are not in the 115 lists: the sentences were changed.
- 𫣆兜 said by 阿傑 and 阿舅 about the factory to people outside it → 𠊎兜 (P61 twice, P63).
- 你个間房 → 若間房 (kaga115 若房間, MOE 若間房). 該位 is "that place": "that person" is 該儕 (11 kaga115).
- A-in has a job (lesson 100): "a girl from my sister's class" → "from the class next door" (P57).
- 寒假 was used in the review lesson without being taught → 寒天放尞.
- 接嘴 is "take up what someone said and go on" (list), not "cut in"; glosses fixed.
- Notes: 拗 is from 進修 29, 地理先生 from 進修 12; line 4 of P59 has 尞天穿.
- Sam's essay: P57 said "the Hakka overseas", P59 is on customs → P57 now says traditions, with reading on the
  Hakka overseas.
- P63: six exercises copied lines of the batch → new sentences. P58: one fill copied a clause of the text.
- Flags in a draft are separated by spaces ("check ok:rule-id"); with a comma the tool drops `check`.
