#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a static, offline-first Japanese N5 learning website.

Run:  python generate_site.py
Produces:
  index.html, hiragana.html, katakana.html, vocab.html,
  grammar.html, kanji.html, quiz.html,
  assets/style.css, assets/app.js, assets/data.js
"""
import os
import json

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "site")
ASSETS = os.path.join(SITE, "assets")
os.makedirs(ASSETS, exist_ok=True)
os.makedirs(os.path.join(ROOT, ".github", "instructions"), exist_ok=True)

# ----------------------------------------------------------------------
# DATA
# ----------------------------------------------------------------------
HIRA = [
    ("あ行", [("a", "あ"), ("i", "い"), ("u", "う"), ("e", "え"), ("o", "お")]),
    ("か行", [("ka", "か"), ("ki", "き"), ("ku", "く"), ("ke", "け"), ("ko", "こ")]),
    ("さ行", [("sa", "さ"), ("shi", "し"), ("su", "す"), ("se", "せ"), ("so", "そ")]),
    ("た行", [("ta", "た"), ("chi", "ち"), ("tsu", "つ"), ("te", "て"), ("to", "と")]),
    ("な行", [("na", "な"), ("ni", "に"), ("nu", "ぬ"), ("ne", "ね"), ("no", "の")]),
    ("は行", [("ha", "は"), ("hi", "ひ"), ("fu", "ふ"), ("he", "へ"), ("ho", "ほ")]),
    ("ま行", [("ma", "ま"), ("mi", "み"), ("mu", "む"), ("me", "め"), ("mo", "も")]),
    ("や行", [("ya", "や"), ("", ""), ("yu", "ゆ"), ("", ""), ("yo", "よ")]),
    ("ら行", [("ra", "ら"), ("ri", "り"), ("ru", "る"), ("re", "れ"), ("ro", "ろ")]),
    ("わ行", [("wa", "わ"), ("", ""), ("", ""), ("", ""), ("wo", "を")]),
    ("ん",   [("n", "ん"), ("", ""), ("", ""), ("", ""), ("", "")]),
]
HIRA_DAKU = [
    ("が行", [("ga", "が"), ("gi", "ぎ"), ("gu", "ぐ"), ("ge", "げ"), ("go", "ご")]),
    ("ざ行", [("za", "ざ"), ("ji", "じ"), ("zu", "ず"), ("ze", "ぜ"), ("zo", "ぞ")]),
    ("だ行", [("da", "だ"), ("ji", "ぢ"), ("zu", "づ"), ("de", "で"), ("do", "ど")]),
    ("ば行", [("ba", "ば"), ("bi", "び"), ("bu", "ぶ"), ("be", "べ"), ("bo", "ぼ")]),
    ("ぱ行", [("pa", "ぱ"), ("pi", "ぴ"), ("pu", "ぷ"), ("pe", "ぺ"), ("po", "ぽ")]),
]
HIRA_YOON = [
    ("拗音 (や行)", [("kya", "きゃ"), ("kyu", "きゅ"), ("kyo", "きょ"), ("sha", "しゃ"),
                   ("shu", "しゅ"), ("sho", "しょ"), ("cha", "ちゃ"), ("chu", "ちゅ"),
                   ("cho", "ちょ"), ("nya", "にゃ"), ("nyu", "にゅ"), ("nyo", "にょ")]),
    ("拗音 (ら行)", [("rya", "りゃ"), ("ryu", "りゅ"), ("ryo", "りょ"), ("hya", "ひゃ"),
                   ("hyu", "ひゅ"), ("hyo", "ひょ"), ("mya", "みゃ"), ("myu", "みゅ"),
                   ("myo", "みょ"), ("gya", "ぎゃ"), ("gyu", "ぎゅ"), ("gyo", "ぎょ")]),
    ("拗音 (ば/ぱ)", [("bya", "びゃ"), ("byu", "びゅ"), ("byo", "びょ"), ("pya", "ぴゃ"),
                   ("pyu", "ぴゅ"), ("pyo", "ぴょ"), ("ja", "じゃ"), ("ju", "じゅ"),
                   ("jo", "じょ"), ("", ""), ("", ""), ("", "")]),
]

KATA = [
    ("ア行", [("a", "ア"), ("i", "イ"), ("u", "ウ"), ("e", "エ"), ("o", "オ")]),
    ("カ行", [("ka", "カ"), ("ki", "キ"), ("ku", "ク"), ("ke", "ケ"), ("ko", "コ")]),
    ("サ行", [("sa", "サ"), ("shi", "シ"), ("su", "ス"), ("se", "セ"), ("so", "ソ")]),
    ("タ行", [("ta", "タ"), ("chi", "チ"), ("tsu", "ツ"), ("te", "テ"), ("to", "ト")]),
    ("ナ行", [("na", "ナ"), ("ni", "ニ"), ("nu", "ヌ"), ("ne", "ネ"), ("no", "ノ")]),
    ("ハ行", [("ha", "ハ"), ("hi", "ヒ"), ("fu", "フ"), ("he", "ヘ"), ("ho", "ホ")]),
    ("マ行", [("ma", "マ"), ("mi", "ミ"), ("mu", "ム"), ("me", "メ"), ("mo", "モ")]),
    ("ヤ行", [("ya", "ヤ"), ("", ""), ("yu", "ユ"), ("", ""), ("yo", "ヨ")]),
    ("ラ行", [("ra", "ラ"), ("ri", "リ"), ("ru", "ル"), ("re", "レ"), ("ro", "ロ")]),
    ("ワ行", [("wa", "ワ"), ("", ""), ("", ""), ("", ""), ("wo", "ヲ")]),
    ("ン",   [("n", "ン"), ("", ""), ("", ""), ("", ""), ("", "")]),
]
KATA_DAKU = [
    ("ガ行", [("ga", "ガ"), ("gi", "ギ"), ("gu", "グ"), ("ge", "ゲ"), ("go", "ゴ")]),
    ("ザ行", [("za", "ザ"), ("ji", "ジ"), ("zu", "ズ"), ("ze", "ゼ"), ("zo", "ゾ")]),
    ("ダ行", [("da", "ダ"), ("ji", "ヂ"), ("zu", "ヅ"), ("de", "デ"), ("do", "ド")]),
    ("バ行", [("ba", "バ"), ("bi", "ビ"), ("bu", "ブ"), ("be", "ベ"), ("bo", "ボ")]),
    ("パ行", [("pa", "パ"), ("pi", "ピ"), ("pu", "プ"), ("pe", "ペ"), ("po", "ポ")]),
]
KATA_YOON = HIRA_YOON  # same romaji structure, rendered with katakana below

# VOCAB: (japanese, romaji, vietnamese, category)
VOCAB = [
    ("私", "watashi", "tôi", "đại từ"),
    ("あなた", "anata", "bạn", "đại từ"),
    ("彼", "kare", "anh ấy", "đại từ"),
    ("彼女", "kanojo", "cô ấy", "đại từ"),
    ("先生", "sensei", "giáo viên", "danh từ"),
    ("学生", "gakusei", "học sinh, sinh viên", "danh từ"),
    ("友達", "tomodachi", "bạn bè", "danh từ"),
    ("家族", "kazoku", "gia đình", "danh từ"),
    ("父", "chichi", "bố (nói về bố mình)", "danh từ"),
    ("母", "haha", "mẹ", "danh từ"),
    ("兄", "ani", "anh trai", "danh từ"),
    ("姉", "ane", "chị gái", "danh từ"),
    ("弟", "otouto", "em trai", "danh từ"),
    ("妹", "imouto", "em gái", "danh từ"),
    ("人", "hito", "người", "danh từ"),
    ("子供", "kodomo", "trẻ em", "danh từ"),
    ("男", "otoko", "đàn ông", "danh từ"),
    ("女", "onna", "phụ nữ", "danh từ"),
    ("水", "mizu", "nước", "danh từ"),
    ("お茶", "ocha", "trà", "danh từ"),
    ("ご飯", "gohan", "cơm, bữa ăn", "danh từ"),
    ("パン", "pan", "bánh mì", "danh từ"),
    ("魚", "sakana", "cá", "danh từ"),
    ("肉", "niku", "thịt", "danh từ"),
    ("卵", "tamago", "trứng", "danh từ"),
    ("野菜", "yasai", "rau", "danh từ"),
    ("果物", "kudamono", "hoa quả", "danh từ"),
    ("りんご", "ringo", "táo", "danh từ"),
    ("バナナ", "banana", "chuối", "danh từ"),
    ("本", "hon", "sách", "danh từ"),
    ("ペン", "pen", "bút", "danh từ"),
    ("鉛筆", "enpitsu", "bút chì", "danh từ"),
    ("車", "kuruma", "xe hơi", "danh từ"),
    ("電車", "densha", "tàu điện", "danh từ"),
    ("バス", "basu", "xe buýt", "danh từ"),
    ("空港", "kuukou", "sân bay", "danh từ"),
    ("駅", "eki", "ga tàu", "danh từ"),
    ("家", "ie", "nhà", "danh từ"),
    ("部屋", "heya", "phòng", "danh từ"),
    ("学校", "gakkou", "trường học", "danh từ"),
    ("会社", "kaisha", "công ty", "danh từ"),
    ("店", "mise", "cửa hàng", "danh từ"),
    ("病院", "byouin", "bệnh viện", "danh từ"),
    ("町", "machi", "thị trấn", "danh từ"),
    ("国", "kuni", "đất nước", "danh từ"),
    ("日本", "nippon", "Nhật Bản", "danh từ"),
    ("名前", "namae", "tên", "danh từ"),
    ("時間", "jikan", "thời gian", "danh từ"),
    ("朝", "asa", "buổi sáng", "danh từ"),
    ("昼", "hiru", "buổi trưa", "danh từ"),
    ("晩", "ban", "buổi tối", "danh từ"),
    ("今日", "kyou", "hôm nay", "danh từ"),
    ("明日", "ashita", "ngày mai", "danh từ"),
    ("昨日", "kinou", "hôm qua", "danh từ"),
    ("年", "toshi", "năm", "danh từ"),
    ("お金", "okane", "tiền", "danh từ"),
    ("仕事", "shigoto", "công việc", "danh từ"),
    ("言葉", "kotoba", "từ, ngôn ngữ", "danh từ"),
    ("色", "iro", "màu sắc", "danh từ"),
    ("赤", "aka", "đỏ", "màu"),
    ("青", "ao", "xanh", "màu"),
    ("白", "shiro", "trắng", "màu"),
    ("黒", "kuro", "đen", "màu"),
    ("犬", "inu", "chó", "danh từ"),
    ("猫", "neko", "mèo", "danh từ"),
    ("鳥", "tori", "chim", "danh từ"),
    ("花", "hana", "hoa", "danh từ"),
    ("木", "ki", "cây", "danh từ"),
    ("山", "yama", "núi", "danh từ"),
    ("川", "kawa", "sông", "danh từ"),
    ("天気", "tenki", "thời tiết", "danh từ"),
    ("雨", "ame", "mưa", "danh từ"),
    ("雪", "yuki", "tuyết", "danh từ"),
    ("風", "kaze", "gió", "danh từ"),
    ("一", "ichi", "một", "số"),
    ("二", "ni", "hai", "số"),
    ("三", "san", "ba", "số"),
    ("四", "shi/yon", "bốn", "số"),
    ("五", "go", "năm", "số"),
    ("六", "roku", "sáu", "số"),
    ("七", "shichi/nana", "bảy", "số"),
    ("八", "hachi", "tám", "số"),
    ("九", "kyuu", "chín", "số"),
    ("十", "juu", "mười", "số"),
    ("行く", "iku", "đi", "động từ"),
    ("来る", "kuru", "đến", "động từ"),
    ("帰る", "kaeru", "về", "động từ"),
    ("食べる", "taberu", "ăn (thể る)", "động từ"),
    ("飲む", "nomu", "uống", "động từ"),
    ("見る", "miru", "nhìn", "động từ"),
    ("聞く", "kiku", "nghe", "động từ"),
    ("話す", "hanasu", "nói", "động từ"),
    ("読む", "yomu", "đọc", "động từ"),
    ("書く", "kaku", "viết", "động từ"),
    ("買う", "kau", "mua", "động từ"),
    ("売る", "uru", "bán", "động từ"),
    ("する", "suru", "làm", "động từ"),
    ("分かる", "wakaru", "hiểu", "động từ"),
    ("ある", "aru", "có (vật)", "động từ"),
    ("いる", "iru", "có (người/động vật)", "động từ"),
    ("勉強する", "benkyou suru", "học", "động từ"),
    ("働く", "hataraku", "làm việc", "động từ"),
    ("大きい", "ookii", "to", "い-adj"),
    ("小さい", "chiisai", "nhỏ", "い-adj"),
    ("新しい", "atarashii", "mới", "い-adj"),
    ("古い", "furui", "cũ", "い-adj"),
    ("高い", "takai", "cao, đắt", "い-adj"),
    ("安い", "yasui", "rẻ", "い-adj"),
    ("良い", "ii", "tốt", "い-adj"),
    ("悪い", "warui", "xấu", "い-adj"),
    ("暑い", "atsui", "nóng (thời tiết)", "い-adj"),
    ("寒い", "samui", "lạnh", "い-adj"),
    ("美味しい", "oishii", "ngon", "い-adj"),
    ("楽しい", "tanoshii", "vui", "い-adj"),
    ("忙しい", "isogashii", "bận", "い-adj"),
    ("静か", "shizuka", "yên tĩnh", "な-adj"),
    ("元気", "genki", "khỏe", "な-adj"),
    ("好き", "suki", "thích", "な-adj"),
    ("嫌い", "kirai", "ghét", "な-adj"),
    ("便利", "benri", "tiện lợi", "な-adj"),
    ("はい", "hai", "vâng", "phó từ"),
    ("いいえ", "iie", "không", "phó từ"),
    ("よく", "yoku", "thường xuyên", "phó từ"),
    ("時々", "tokidoki", "thỉnh thoảng", "phó từ"),
    ("いつも", "itsumo", "luôn", "phó từ"),
    ("そして", "soshite", "và, rồi", "kết từ"),
    ("でも", "demo", "nhưng", "kết từ"),
    ("と", "to", "và (nối danh từ)", "trợ từ"),
    ("ね", "ne", "nhé (cuối câu)", "trợ từ"),
    ("よ", "yo", "ơ (nhấn mạnh)", "trợ từ"),
]

# GRAMMAR: (pattern, explanation, example)
GRAMMAR = [
    ("〜は〜です", "Khẳng định: Chủ ngữ は Danh từ です", "私は学生です。 (Tôi là sinh viên.)"),
    ("〜は〜ではありません", "Phủ định: Chủ ngữ は Danh từ ではありません", "彼は先生ではありません。 (Anh ấy không phải giáo viên.)"),
    ("〜は〜ですか", "Nghi vấn: Chủ ngữ は Danh từ ですか", "これは本ですか。 (Đây là sách phải không?)"),
    ("を", "Đánh dấu tân ngữ trực tiếp", "水を飲みます。 (Uống nước.)"),
    ("に", "Đánh dấu thời gian / đích đến", "学校に行きます。 (Đi đến trường.)"),
    ("で", "Đánh dấu nơi xảy ra hành động", "図書館で勉強します。 (Học ở thư viện.)"),
    ("と", "Nối danh từ: 'và'", "私と友達 (Tôi và bạn)"),
    ("も", "'cũng' thay cho は", "私も学生です。 (Tôi cũng là sinh viên.)"),
    ("の", "Sở hữu: A の B (B của A)", "私の本 (Sách của tôi)"),
    ("これ/それ/あれ", "Chỉ từ: này / kia / kia (xa)", "これはペンです。 (Đây là bút.)"),
    ("だれ/なに/どこ", "Nghi vấn: ai / cái gì / ở đâu", "名前はなんですか。 (Tên là gì?)"),
    ("い形容詞", "Thêm です ở cuối; phủ định くないです", "高いです。/高くないです。 (Đắt./Không đắt.)"),
    ("な形容詞", "Thêm な trước danh từ; です ở cuối", "静かな部屋 (Phòng yên tĩnh)"),
    ("〜ます/〜ました", "Thể lịch sự hiện tại / quá khứ", "食べます。/食べました。 (Ăn./Đã ăn.)"),
    ("〜ません/〜ませんでした", "Phủ định lịch sự hiện tại / quá khứ", "行きません。/行きませんでした。"),
    ("て形", "Nối câu / cầu xin: てください", "本を読んでください。 (Hãy đọc sách.)"),
    ("たい", "Muốn làm: Động từ bỏ ます + たい", "水が飲みたいです。 (Muốn uống nước.)"),
    ("ことができる", "Có thể: Động từ bỏ ます + ことができる", "日本語が話せます。 (Có thể nói tiếng Nhật.)"),
    ("から", "Nguyên nhân: câu + から", "忙しいから、行きません。 (Vì bận nên không đi.)"),
    ("ば", "Điều kiện: tính từ/động từ + ば", "安ければ、買います。 (Nếu rẻ thì mua.)"),
    ("数 で", "Đếm: danh từ + số + đơn vị", "三冊の本 (3 quyển sách)"),
    ("た (quá khứ)", "Quá khứ: động từ thể た", "行きました → 行った (đã đi)"),
    ("ない (phủ định)", "Phủ định thân mật: bỏ ます + ない", "食べない (không ăn)"),
    ("なさい", "Mệnh lệnh nhẹ: て + なさい", "早く寝なさい。 (Hãy đi ngủ sớm.)"),
    ("より", "So sánh hơn: A は B より ~", "犬は猫より大きい。 (Chó lớn hơn mèo.)"),
    ("一番", "So sánh nhất: ~の中で一番~", "一番高い (đắt nhất)"),
    ("に行く", "Mục đích: に + động từ thể ます + に行く", "買い物に行きます。 (Đi mua sắm.)"),
]

# KANJI: (kanji, reading, meaning, example)
KANJI = [
    ("一", "いち", "nhất (one)", "一日 ichi-nichi: một ngày"),
    ("二", "に", "hai (two)", "二月 ni-gatsu: tháng hai"),
    ("三", "さん", "ba (three)", "三日 san-nichi: mồng ba"),
    ("四", "し/よん", "bốn (four)", "四時 yo-ji: 4 giờ"),
    ("五", "ご", "năm (five)", "五日 go-nichi: mồng năm"),
    ("六", "ろく", "sáu (six)", "六日 roku-nichi: ngày sáu"),
    ("七", "しち/なな", "bảy (seven)", "七時 shichi-ji: 7 giờ"),
    ("八", "はち", "tám (eight)", "八日 hachi-nichi: ngày tám"),
    ("九", "きゅう", "chín (nine)", "九時 kyuu-ji: 9 giờ"),
    ("十", "じゅう", "mười (ten)", "十日 juu-nichi: ngày mười"),
    ("百", "ひゃく", "trăm (hundred)", "三百 san-byaku: 300"),
    ("千", "せん", "nghìn (thousand)", "二千 ni-sen: 2000"),
    ("万", "まん", "vạn (ten thousand)", "一万 ichi-man: 10000"),
    ("人", "じん/にん", "người (person)", "日本人 nippon-jin: người Nhật"),
    ("子", "こ", "trẻ em (child)", "子供 kodomo: trẻ em"),
    ("女", "じょ/おんな", "nữ (woman)", "女の子 onna-no-ko: bé gái"),
    ("男", "だん/おとこ", "nam (man)", "男の子 otoko-no-ko: bé trai"),
    ("父", "ふう/ちち", "bố (father)", "父親 chichi-oya: bố"),
    ("母", "ぼ/はは", "mẹ (mother)", "母親 haha-oya: mẹ"),
    ("友", "ゆう", "bạn (friend)", "友達 tomodachi: bạn bè"),
    ("学", "がく", "học (study)", "学生 gakusei: sinh viên"),
    ("生", "せい/しょう", "sống/sinh (life)", "先生 sensei: giáo viên"),
    ("校", "こう", "trường (school)", "学校 gakkou: trường học"),
    ("先", "せん", "trước (before)", "先生 sensei"),
    ("日", "にち/び", "ngày/mặt trời (day/sun)", "日曜日 nichiyoubi: Chủ nhật"),
    ("月", "げつ/つき", "tháng/trăng (month)", "月曜日 getsuyoubi: Thứ hai"),
    ("火", "か", "lửa (fire)", "火曜日 kayoubi: Thứ ba"),
    ("水", "すい", "nước (water)", "水曜日 suiyoubi: Thứ tư"),
    ("木", "もく/き", "cây/gỗ (tree)", "木曜日 mokuyoubi: Thứ năm"),
    ("金", "きん", "vàng/tiền (gold)", "金曜日 kinyoubi: Thứ sáu"),
    ("土", "ど/つち", "đất (earth)", "土曜日 doyoubi: Thứ bảy"),
    ("山", "さん/やま", "núi (mountain)", "山 yama: núi"),
    ("川", "せん/かわ", "sông (river)", "川 kawa: sông"),
    ("田", "でん/た", "ruộng (rice field)", "田んぼ tanbo: ruộng lúa"),
    ("目", "もく/め", "mắt (eye)", "目 me: mắt"),
    ("口", "こう/くち", "miệng (mouth)", "口 kuchi: miệng"),
    ("耳", "じ/みみ", "tai (ear)", "耳 mimi: tai"),
    ("手", "しゅ/て", "tay (hand)", "手 te: tay"),
    ("足", "そく/あし", "chân (foot)", "足 ashi: chân"),
    ("車", "しゃ/くるま", "xe (car)", "電車 densha: tàu điện"),
    ("門", "もん", "cửa (gate)", "門 mon: cổng"),
    ("雨", "う", "mưa (rain)", "雨 ame: mưa"),
    ("電", "でん", "điện (electric)", "電車 densha"),
    ("気", "き", "khí/tinh thần (spirit)", "天気 tenki: thời tiết"),
    ("空", "くう/そら", "trời (sky)", "空港 kuukou: sân bay"),
    ("花", "か/はな", "hoa (flower)", "花 hana: hoa"),
    ("虫", "ちゅう/むし", "côn trùng (insect)", "虫 mushi: côn trùng"),
    ("魚", "ぎょ/さかな", "cá (fish)", "魚 sakana: cá"),
    ("鳥", "ちょう/とり", "chim (bird)", "鳥 tori: chim"),
    ("犬", "けん/いぬ", "chó (dog)", "犬 inu: chó"),
    ("猫", "びょう/ねこ", "mèo (cat)", "猫 neko: mèo"),
    ("食", "しょく", "ăn (eat)", "食べ物 tabemono: đồ ăn"),
    ("飲", "いん", "uống (drink)", "飲み物 nomimono: đồ uống"),
    ("見", "けん/み", "nhìn (see)", "見る miru: nhìn"),
    ("書", "しょ", "viết (write)", "書く kaku: viết"),
    ("読", "どく", "đọc (read)", "読む yomu: đọc"),
    ("話", "わ", "nói (speak)", "話す hanasu: nói"),
    ("行", "こう/ぎょう", "đi (go)", "行く iku: đi"),
    ("来", "らい", "đến (come)", "来る kuru: đến"),
    ("出", "しゅつ", "ra (exit)", "出る deru: ra"),
    ("入", "にゅう", "vào (enter)", "入る hairu: vào"),
    ("立", "りつ", "đứng (stand)", "立つ tatsu: đứng"),
    ("休", "きゅう", "nghỉ (rest)", "休む yasumu: nghỉ"),
    ("買", "ばい", "mua (buy)", "買う kau: mua"),
    ("売", "ばい", "bán (sell)", "売る uru: bán"),
    ("高", "こう/たか", "cao/đắt (high)", "高い takai: cao/đắt"),
    ("安", "あん/やす", "rẻ (cheap)", "安い yasui: rẻ"),
    ("新", "しん/あたら", "mới (new)", "新しい atarashii: mới"),
    ("古", "こ/ふる", "cũ (old)", "古い furui: cũ"),
    ("白", "はく/しろ", "trắng (white)", "白い shiroi: trắng"),
    ("黒", "こく/くろ", "đen (black)", "黒い kuroi: đen"),
    ("赤", "せき/あか", "đỏ (red)", "赤い akai: đỏ"),
    ("青", "せい/あお", "xanh (blue)", "青い aoi: xanh"),
    ("名", "めい/な", "tên (name)", "名前 namae: tên"),
    ("時", "じ", "thời gian/giờ (time)", "時間 jikan: thời gian"),
    ("年", "ねん", "năm (year)", "今年 kotoshi: năm nay"),
    ("中", "ちゅう/なか", "trong (inside)", "中国 chuugoku: Trung Quốc"),
    ("外", "がい/そと", "ngoài (outside)", "外 soto: ngoài"),
    ("上", "じょう/うえ", "trên (above)", "上 ue: trên"),
    ("下", "か/した", "dưới (below)", "下 shita: dưới"),
    ("右", "う/みぎ", "phải (right)", "右 migi: phải"),
    ("左", "さ/ひだり", "trái (left)", "左 hidari: trái"),
    ("前", "ぜん/まえ", "trước (front)", "前 mae: trước"),
    ("後", "ご/うしろ", "sau (back)", "後 ushiro: sau"),
    ("東", "とう/ひがし", "đông (east)", "東 higashi: đông"),
    ("西", "せい/にし", "tây (west)", "西 nishi: tây"),
    ("南", "なん/みなみ", "nam (south)", "南 minami: nam"),
    ("北", "ほく/きた", "bắc (north)", "北 kita: bắc"),
    ("本", "ほん", "sách/gốc (book)", "本 hon: sách"),
    ("文", "ぶん", "văn/câu (sentence)", "日本語 nihongo: tiếng Nhật"),
    ("字", "じ", "chữ (character)", "文字 moji: chữ"),
    ("語", "ご", "ngôn ngữ (language)", "日本語 nihongo"),
    ("国", "こく/くに", "nước (country)", "日本国 nippon-koku: nước Nhật"),
    ("会社", "かいしゃ", "công ty (company)", "会社員 kaishain: nhân viên"),
    ("店", "てん/みせ", "cửa hàng (shop)", "店 mise: cửa hàng"),
    ("道", "どう/みち", "đường (road)", "道 michi: đường"),
    ("自", "じ", "tự (self)", "自動車 jidousha: ô tô"),
    ("動", "どう", "động (move)", "自動車 jidousha: ô tô"),
    ("体", "たい/からだ", "cơ thể (body)", "体 karada: cơ thể"),
    ("言", "げん/い", "nói (say)", "言葉 kotoba: lời nói"),
    ("思", "し/おも", "nghĩ (think)", "思う omou: nghĩ"),
    ("知", "ち/し", "biết (know)", "知る shiru: biết"),
]

# ----------------------------------------------------------------------
# CSS
# ----------------------------------------------------------------------
CSS = ''':root{
  --indigo:#283593; --indigo-light:#5c6bc0; --red:#c62828;
  --cream:#fdfaf3; --ink:#222; --muted:#666; --line:#e3e0d8;
  --card:#fff; --shadow:0 2px 10px rgba(40,53,147,.08);
}
*{box-sizing:border-box}
body{margin:0;font-family:"Segoe UI",system-ui,"Hiragino Sans",sans-serif;
  background:var(--cream);color:var(--ink);line-height:1.6}
header.top{background:linear-gradient(135deg,var(--indigo),var(--indigo-light));
  color:#fff;padding:28px 20px;text-align:center}
header.top h1{margin:0;font-size:1.9rem;letter-spacing:1px}
header.top p{margin:6px 0 0;opacity:.9}
nav.main{position:sticky;top:0;z-index:10;background:#fff;border-bottom:1px solid var(--line);
  display:flex;flex-wrap:wrap;justify-content:center;gap:4px;padding:8px}
nav.main a{text-decoration:none;color:var(--indigo);padding:8px 14px;border-radius:8px;
  font-weight:600;font-size:.92rem}
nav.main a:hover{background:var(--indigo);color:#fff}
nav.main a.active{background:var(--red);color:#fff}
main{max-width:980px;margin:0 auto;padding:24px 18px 60px}
section{margin-bottom:34px}
h2{color:var(--indigo);border-left:5px solid var(--red);padding-left:12px;margin-top:0}
h3{color:var(--indigo-light)}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:16px 18px;box-shadow:var(--shadow);margin-bottom:14px}
.grid{display:grid;gap:14px}
.grid.cols-2{grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}
.grid.cols-3{grid-template-columns:repeat(auto-fill,minmax(180px,1fr))}
.grid.cols-4{grid-template-columns:repeat(auto-fill,minmax(140px,1fr))}
.kana-table{border-collapse:collapse;width:100%;max-width:640px;margin:10px 0}
.kana-table th,.kana-table td{border:1px solid var(--line);padding:10px;text-align:center}
.kana-table th{background:var(--indigo);color:#fff;width:70px}
.kana-table td.empty{background:#f3f1ea}
.kana{display:block;font-size:1.7rem;line-height:1.1}
.roma{display:block;font-size:.75rem;color:var(--muted)}
.vocab-row,.grammar-row,.kanji-card{padding:10px 12px;border:1px solid var(--line);
  border-radius:10px;background:#fff}
.jp{font-size:1.4rem;font-weight:700;color:var(--indigo)}
.romaji{color:var(--red);font-style:italic;margin-left:8px}
.cat{display:inline-block;font-size:.7rem;background:#eee;color:#555;border-radius:6px;
  padding:1px 7px;margin-top:4px}
.kanji-big{font-size:2.6rem;text-align:center;color:var(--indigo)}
.filter{margin:10px 0 18px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.filter input,.filter select{padding:8px 10px;border:1px solid var(--line);border-radius:8px;font-size:.95rem}
.btn{background:var(--indigo);color:#fff;border:none;padding:10px 18px;border-radius:8px;
  font-weight:600;cursor:pointer;font-size:.95rem}
.btn:hover{background:var(--red)}
.btn.ghost{background:#fff;color:var(--indigo);border:1px solid var(--indigo)}
#quiz-box{background:#fff;border:1px solid var(--line);border-radius:12px;padding:22px;
  box-shadow:var(--shadow);text-align:center}
#q-jp{font-size:2.4rem;color:var(--indigo);margin:10px 0}
#q-opts{display:grid;gap:10px;max-width:420px;margin:16px auto}
.opt{padding:12px;border:1px solid var(--line);border-radius:10px;cursor:pointer;background:#fff;font-size:1rem}
.opt:hover{border-color:var(--indigo)}
.opt.correct{background:#e8f5e9;border-color:#43a047}
.opt.wrong{background:#ffebee;border-color:#e53935}
#q-score{font-weight:700;color:var(--red)}
footer{text-align:center;color:var(--muted);font-size:.85rem;padding:20px;border-top:1px solid var(--line)}
.tag{display:inline-block;background:var(--indigo-light);color:#fff;border-radius:6px;padding:2px 8px;font-size:.75rem;margin-right:6px}
ul.clean{margin:6px 0;padding-left:20px}
ul.clean li{margin:4px 0}
.card{transition:transform .15s ease, box-shadow .15s ease}
.card:hover{transform:translateY(-3px);box-shadow:0 6px 18px rgba(40,53,147,.14)}
nav.main a{transition:background .15s,color .15s}
/* Hamburger + responsive */
.menu-toggle{display:none;background:var(--indigo);color:#fff;border:none;font-size:1rem;
  font-weight:700;padding:10px 14px;cursor:pointer;border-radius:8px;position:sticky;top:0;z-index:11;width:100%}
@media (max-width:720px){
  nav.main{flex-direction:column;align-items:stretch;display:none;padding:4px}
  nav.main.open{display:flex}
  nav.main a{text-align:center;margin:2px 0}
  .menu-toggle{display:block}
  header.top h1{font-size:1.4rem}
  header.top p{font-size:.8rem}
  main{padding:16px 12px 50px}
  .grid.cols-2,.grid.cols-3,.grid.cols-4{grid-template-columns:1fr}
  .kana-table{font-size:.82rem}
  .kana{font-size:1.3rem}
  .jp{font-size:1.2rem}
}
'''

# ----------------------------------------------------------------------
# JS (data + app)
# ----------------------------------------------------------------------
DATA_JS = "const VOCAB = " + json.dumps(VOCAB, ensure_ascii=False) + ";\n" + \
          "const GRAMMAR = " + json.dumps(GRAMMAR, ensure_ascii=False) + ";\n" + \
          "const KANJI = " + json.dumps(KANJI, ensure_ascii=False) + ";\n"

APP_JS = r'''
// ---- Vocabulary filter (vocab.html) ----
function initVocabFilter(){
  var box = document.getElementById('vocab-list');
  if(!box) return;
  var q = document.getElementById('v-search');
  var c = document.getElementById('v-cat');
  function cats(){
    var s = new Set(VOCAB.map(function(v){return v[3];}));
    s.forEach(function(x){ var o=document.createElement('option'); o.value=x; o.textContent=x; c.appendChild(o); });
  }
  cats();
  function render(){
    var term = (q.value||'').toLowerCase();
    var cat = c.value;
    box.innerHTML = '';
    VOCAB.filter(function(v){
      return (!cat || v[3]===cat) &&
        (v[0].toLowerCase().indexOf(term)>=0 || v[1].toLowerCase().indexOf(term)>=0 || v[2].toLowerCase().indexOf(term)>=0);
    }).forEach(function(v){
      var d=document.createElement('div'); d.className='vocab-row';
      d.innerHTML='<span class="jp">'+v[0]+'</span><span class="romaji">'+v[1]+'</span>'+
        '<div>'+v[2]+'<span class="cat">'+v[3]+'</span></div>';
      box.appendChild(d);
    });
  }
  q.addEventListener('input', render);
  c.addEventListener('change', render);
  render();
}

// ---- Quiz (quiz.html) ---- diverse + random questions & answers ----
var QUIZ = {idx:0, score:0, total:0};
function shuffle(a){ for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=a[i];a[i]=a[j];a[j]=t;} return a; }
function pickOpts(correct, pool){
  var opts=new Set([correct]);
  while(opts.size<4){ var r=pool[Math.floor(Math.random()*pool.length)]; if(r && r!==correct) opts.add(r); }
  return shuffle(Array.from(opts));
}
function makeQuestion(){
  var types=['jp2vi','vi2jp','jp2ro','ro2jp','gram'];
  var t=types[Math.floor(Math.random()*types.length)];
  if(t==='gram'){
    var g=GRAMMAR[Math.floor(Math.random()*GRAMMAR.length)];
    return {label:'Ngữ pháp', prompt:'Mẫu nào có nghĩa: "'+g[1]+'"?',
      options:pickOpts(g[0], GRAMMAR.map(function(x){return x[0];})), answer:g[0]};
  }
  var v=VOCAB[Math.floor(Math.random()*VOCAB.length)];
  if(t==='jp2vi') return {label:'Từ vựng', prompt:'「'+v[0]+'」 ('+v[1]+') nghĩa là?',
      options:pickOpts(v[2], VOCAB.map(function(x){return x[2];})), answer:v[2]};
  if(t==='vi2jp') return {label:'Từ vựng', prompt:'Tiếng Nhật của "'+v[2]+'"?',
      options:pickOpts(v[0], VOCAB.map(function(x){return x[0];})), answer:v[0]};
  if(t==='jp2ro') return {label:'Phát âm', prompt:'Romaji của 「'+v[0]+'」?',
      options:pickOpts(v[1], VOCAB.map(function(x){return x[1];})), answer:v[1]};
  return {label:'Từ vựng', prompt:'Từ có romaji "'+v[1]+'" là?',
      options:pickOpts(v[0], VOCAB.map(function(x){return x[0];})), answer:v[0]};
}
function nextQuestion(){
  var box=document.getElementById('q-opts');
  var jp=document.getElementById('q-jp');
  var typeEl=document.getElementById('q-type');
  if(QUIZ.idx>=10){
    jp.textContent='🎉';
    typeEl.textContent='';
    box.innerHTML='<p style="font-size:1.2rem">Hoàn thành! Điểm: <span id="q-score">'+QUIZ.score+'/'+QUIZ.total+'</span></p>';
    return;
  }
  var q=makeQuestion();
  typeEl.textContent=q.label;
  jp.textContent=q.prompt;
  box.innerHTML='';
  q.options.forEach(function(o){
    var b=document.createElement('div'); b.className='opt'; b.textContent=o;
    b.onclick=function(){
      QUIZ.total++;
      if(o===q.answer){ b.classList.add('correct'); QUIZ.score++; }
      else { b.classList.add('wrong'); }
      Array.prototype.forEach.call(box.children,function(ch){ ch.onclick=null; if(ch.textContent===q.answer) ch.classList.add('correct'); });
      QUIZ.idx++;
      setTimeout(nextQuestion, 700);
    };
    box.appendChild(b);
  });
  document.getElementById('q-progress').textContent='Câu '+(QUIZ.idx+1)+'/10';
}
function initQuiz(){
  if(!document.getElementById('q-opts')) return;
  document.getElementById('q-restart').onclick=function(){ QUIZ={idx:0,score:0,total:0}; nextQuestion(); };
  nextQuestion();
}
document.addEventListener('DOMContentLoaded', function(){ initVocabFilter(); initQuiz(); });
'''

# ----------------------------------------------------------------------
# HTML builders
# ----------------------------------------------------------------------
NAV = [
    ("index.html", "Trang chủ"),
    ("hiragana.html", "Hiragana"),
    ("katakana.html", "Katakana"),
    ("vocab.html", "Từ vựng"),
    ("grammar.html", "Ngữ pháp"),
    ("kanji.html", "Kanji"),
    ("quiz.html", "Trắc nghiệm"),
]


def page(title, active, body):
    nav_html = "".join(
        '<a href="%s"%s>%s</a>' % (href, ' class="active"' if href == active else "", label)
        for href, label in NAV
    )
    return """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s — Nhật N5</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="top">
  <h1>日本語 N5 — Học tiếng Nhật sơ cấp</h1>
  <p>Website tĩnh, học offline · Hiragana · Katakana · Từ vựng · Ngữ pháp · Kanji · Trắc nghiệm</p>
</header>
<button class="menu-toggle" aria-label="Menu" onclick="document.querySelector('nav.main').classList.toggle('open')">☰ Menu</button>
<nav class="main">%s</nav>
<main>
%s
</main>
<footer>Được tạo bởi AIOS Planner · Nội dung mang tính tham khảo luyện thi JLPT N5.</footer>
<script src="assets/data.js"></script>
<script src="assets/app.js"></script>
</body>
</html>
""" % (title, nav_html, body)


def kana_table(rows):
    out = []
    for label, items in rows:
        cells = "<th>%s</th>" % label
        for roma, cha in items:
            if cha:
                cells += '<td><span class="kana">%s</span><span class="roma">%s</span></td>' % (cha, roma)
            else:
                cells += '<td class="empty"></td>'
        out.append("<tr>%s</tr>" % cells)
    return '<table class="kana-table">%s</table>' % "".join(out)


def build_index():
    body = """
<section>
  <h2>Chào mừng đến với khóa học tiếng Nhật N5</h2>
  <div class="grid cols-3">
    <div class="card"><h3>あ Hiragana</h3><p>Bảng chữ mềm cơ bản và biến âm.</p><a class="btn" href="hiragana.html">Học ngay</a></div>
    <div class="card"><h3>ア Katakana</h3><p>Bảng chữ cứng dùng cho từ mượn.</p><a class="btn" href="katakana.html">Học ngay</a></div>
    <div class="card"><h3>単語 Từ vựng</h3><p>Hơn %d từ vựng N5 thông dụng.</p><a class="btn" href="vocab.html">Học ngay</a></div>
    <div class="card"><h3>文法 Ngữ pháp</h3><p>%d điểm ngữ pháp trọng tâm.</p><a class="btn" href="grammar.html">Học ngay</a></div>
    <div class="card"><h3>漢字 Kanji</h3><p>%d chữ Hán thường gặp trong N5.</p><a class="btn" href="kanji.html">Học ngay</a></div>
    <div class="card"><h3>クイズ Trắc nghiệm</h3><p>Kiểm tra nhanh từ vựng đã học.</p><a class="btn" href="quiz.html">Làm bài</a></div>
  </div>
</section>
<section>
  <h2>Mẹo học N5 hiệu quả</h2>
  <ul class="clean">
    <li>Học Hiragana &amp; Katakana thuộc lòng trước (khoảng 1–2 tuần).</li>
    <li>Ôn từ vựng theo chủ đề, kết hợp flashcard mỗi ngày.</li>
    <li>Nắm chắc các trợ từ は・を・に・で・と・も・の.</li>
    <li>Luyện đọc hiểu ngắn và làm đề thử JLPT mẫu.</li>
  </ul>
</section>
""" % (len(VOCAB), len(GRAMMAR), len(KANJI))
    return page("Trang chủ", "index.html", body)


def build_hiragana():
    body = """
<section><h2>Bảng Hiragana (ひらがな)</h2>
<h3>Cơ bản</h3>%s
<h3>Dakuon &amp; Handakuon (濁音・半濁音)</h3>%s
<h3>Yōon (拗音)</h3>%s
</section>
""" % (kana_table(HIRA), kana_table(HIRA_DAKU), kana_table(HIRA_YOON))
    return page("Hiragana", "hiragana.html", body)


def build_katakana():
    body = """
<section><h2>Bảng Katakana (カタカナ)</h2>
<h3>Cơ bản</h3>%s
<h3>Dakuon &amp; Handakuon (濁音・半濁音)</h3>%s
<h3>Yōon (拗音)</h3>%s
<p class="cat">Katakana dùng chủ yếu cho từ mượn tiếng nước ngoài, tên riêng và onomatopoeia.</p>
</section>
""" % (kana_table(KATA), kana_table(KATA_DAKU), kana_table(KATA_YOON))
    return page("Katakana", "katakana.html", body)


def build_vocab():
    body = """
<section><h2>Từ vựng N5</h2>
<div class="filter">
  <input id="v-search" placeholder="Tìm theo Nhật / romaji / nghĩa...">
  <select id="v-cat"><option value="">-- Tất cả chủ đề --</option></select>
</div>
<div id="vocab-list" class="grid cols-2"></div>
</section>
"""
    return page("Từ vựng", "vocab.html", body)


def build_grammar():
    rows = "".join(
        '<div class="grammar-row"><span class="tag">%d</span><b>%s</b><div>%s</div><div class="romaji">Ví dụ: %s</div></div>'
        % (i + 1, g[0], g[1], g[2]) for i, g in enumerate(GRAMMAR)
    )
    body = '<section><h2>Ngữ pháp N5</h2><div class="grid cols-2">%s</div></section>' % rows
    return page("Ngữ pháp", "grammar.html", body)


def build_kanji():
    cards = "".join(
        '<div class="kanji-card"><div class="kanji-big">%s</div><div><b>Âm:</b> %s</div><div><b>Nghĩa:</b> %s</div><div class="romaji">%s</div></div>'
        % (k[0], k[1], k[2], k[3]) for k in KANJI
    )
    body = '<section><h2>Kanji N5 (%d chữ)</h2><div class="grid cols-4">%s</div></section>' % (len(KANJI), cards)
    return page("Kanji", "kanji.html", body)


def build_quiz():
    body = """
<section><h2>Trắc nghiệm từ vựng</h2>
<div id="quiz-box">
  <div id="q-progress">Câu 1/10</div>
  <div id="q-type" class="tag"></div>
  <div id="q-jp">？</div>
  <div id="q-opts"></div>
  <button id="q-restart" class="btn ghost">Làm lại</button>
</div>
</section>
"""
    return page("Trắc nghiệm", "quiz.html", body)


# ----------------------------------------------------------------------
# Project docs (project-setup-info-local + agent-customization)
# ----------------------------------------------------------------------
README_MD = """# Nhật N5 — Website học tiếng Nhật sơ cấp (JLPT N5)

Website tĩnh, **offline-first**, không cần build. Mở trực tiếp `site/index.html`
hoặc chạy dev server.

## Cấu trúc dự án
- `generate_site.py` — sinh trang (deterministic, KHÔNG dùng LLM)
- `governance_check.py` — validation gate (đầy đủ + xác thực nội dung)
- `site/` — đầu ra tĩnh
  - `index.html`, `hiragana.html`, `katakana.html`, `vocab.html`,
    `grammar.html`, `kanji.html`, `quiz.html`
  - `assets/style.css`, `assets/data.js`, `assets/app.js`
- `.github/instructions/nihongo-n5.instructions.md` — hướng dẫn dự án

## Lệnh
```powershell
python generate_site.py      # sinh lại site/
python serve.py             # dev server http://localhost:8000
python governance_check.py  # chạy governance gate
```

## Nội dung
Hiragana, Katakana, ~%d từ vựng N5, ~%d ngữ pháp, ~%d Kanji,
và trắc nghiệm đa dạng (5 dạng câu hỏi, đáp án random, xáo trộn).
""" % (len(VOCAB), len(GRAMMAR), len(KANJI))

SERVE_PY = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple offline dev server for the generated static site."""
import http.server
import socketserver
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
os.chdir(ROOT)
PORT = 8000
with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
    print("Serving %s at http://localhost:%d" % (ROOT, PORT))
    httpd.serve_forever()
'''

INSTRUCTIONS_MD = """---
description: "Use when working on the Nihongo N5 static learning website under work/20260824-nihongo-n5/"
applyTo: "work/20260824-nihongo-n5/**"
---

# Nhật N5 Website — Project Instructions

Static, offline-first Japanese N5 learning site generated by `generate_site.py`.

## Conventions
- All content data lives in `generate_site.py` (VOCAB, GRAMMAR, KANJI, HIRA, KATA)
  and is emitted to `site/assets/data.js`.
- Pages are built by pure Python functions `build_index()`, `build_hiragana()`, etc.
  Keep them side-effect free (no I/O, no LLM) — deterministic-first.
- Quiz (`site/quiz.html` + `assets/app.js`) must stay diverse: 5 question types
  (jp2vi, vi2jp, jp2ro, ro2jp, gram), 4 random options, shuffled answers.
- UI must be responsive and include a hamburger menu (`.menu-toggle`) for <=720px.
- Never add external CDN / network dependencies — offline-first.
- Regenerate via `python generate_site.py`; validate via `python governance_check.py`.
"""


# ----------------------------------------------------------------------
# Write all
# ----------------------------------------------------------------------
def main():
    files = {
        "index.html": build_index(),
        "hiragana.html": build_hiragana(),
        "katakana.html": build_katakana(),
        "vocab.html": build_vocab(),
        "grammar.html": build_grammar(),
        "kanji.html": build_kanji(),
        "quiz.html": build_quiz(),
    }
    for name, html in files.items():
        with open(os.path.join(SITE, name), "w", encoding="utf-8") as f:
            f.write(html)
    with open(os.path.join(ASSETS, "style.css"), "w", encoding="utf-8") as f:
        f.write(CSS)
    with open(os.path.join(ASSETS, "data.js"), "w", encoding="utf-8") as f:
        f.write(DATA_JS)
    with open(os.path.join(ASSETS, "app.js"), "w", encoding="utf-8") as f:
        f.write(APP_JS)
    with open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8") as f:
        f.write(README_MD)
    with open(os.path.join(ROOT, "serve.py"), "w", encoding="utf-8") as f:
        f.write(SERVE_PY)
    with open(os.path.join(ROOT, ".github", "instructions", "nihongo-n5.instructions.md"), "w", encoding="utf-8") as f:
        f.write(INSTRUCTIONS_MD)
    print("Generated %d HTML pages + assets + README.md + serve.py + instructions" % len(files))


if __name__ == "__main__":
    main()
