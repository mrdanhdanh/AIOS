// Dữ liệu tiếng Nhật N5 — Hiragana, Katakana, Từ vựng, Ngữ pháp
// Nguồn tham khảo: Danh sách từ vựng JLPT N5, bảng chữ cái tiếng Nhật.

const KANA = {
  hiragana: {
    title: "Hiragana (ひらがな)",
    groups: [
      { label: "Cơ bản", items: [
        ["あ","a"],["い","i"],["う","u"],["え","e"],["お","o"],
        ["か","ka"],["き","ki"],["く","ku"],["け","ke"],["こ","ko"],
        ["さ","sa"],["し","shi"],["す","su"],["せ","se"],["そ","so"],
        ["た","ta"],["ち","chi"],["つ","tsu"],["て","te"],["と","to"],
        ["な","na"],["に","ni"],["ぬ","nu"],["ね","ne"],["の","no"],
        ["は","ha"],["ひ","hi"],["ふ","fu"],["へ","he"],["ほ","ho"],
        ["ま","ma"],["み","mi"],["む","mu"],["め","me"],["も","mo"],
        ["や","ya"],["ゆ","yu"],["よ","yo"],
        ["ら","ra"],["り","ri"],["る","ru"],["れ","re"],["ろ","ro"],
        ["わ","wa"],["を","wo"],["ん","n"]
      ]},
      { label: "Dakuten (゛)", items: [
        ["が","ga"],["ぎ","gi"],["ぐ","gu"],["げ","ge"],["ご","go"],
        ["ざ","za"],["じ","ji"],["ず","zu"],["ぜ","ze"],["ぞ","zo"],
        ["だ","da"],["ぢ","ji"],["づ","zu"],["で","de"],["ど","do"],
        ["ば","ba"],["び","bi"],["ぶ","bu"],["べ","be"],["ぼ","bo"],
        ["ぱ","pa"],["ぴ","pi"],["ぷ","pu"],["ぺ","pe"],["ぽ","po"]
      ]},
      { label: "Kết hợp (や・ゆ・よ)", items: [
        ["きゃ","kya"],["きゅ","kyu"],["きょ","kyo"],
        ["しゃ","sha"],["しゅ","shu"],["しょ","sho"],
        ["ちゃ","cha"],["ちゅ","chu"],["ちょ","cho"],
        ["にゃ","nya"],["にゅ","nyu"],["にょ","nyo"],
        ["ひゃ","hya"],["ひゅ","hyu"],["ひょ","hyo"],
        ["みゃ","mya"],["みゅ","myu"],["みょ","myo"],
        ["りゃ","rya"],["りゅ","ryu"],["りょ","ryo"],
        ["ぎゃ","gya"],["ぎゅ","gyu"],["ぎょ","gyo"],
        ["じゃ","ja"],["じゅ","ju"],["じょ","jo"],
        ["びゃ","bya"],["びゅ","byu"],["びょ","byo"],
        ["ぴゃ","pya"],["ぴゅ","pyu"],["ぴょ","pyo"]
      ]}
    ]
  },
  katakana: {
    title: "Katakana (カタカナ)",
    groups: [
      { label: "Cơ bản", items: [
        ["ア","a"],["イ","i"],["ウ","u"],["エ","e"],["オ","o"],
        ["カ","ka"],["キ","ki"],["ク","ku"],["ケ","ke"],["コ","ko"],
        ["サ","sa"],["シ","shi"],["ス","su"],["セ","se"],["ソ","so"],
        ["タ","ta"],["チ","chi"],["ツ","tsu"],["テ","te"],["ト","to"],
        ["ナ","na"],["ニ","ni"],["ヌ","nu"],["ネ","ne"],["ノ","no"],
        ["ハ","ha"],["ヒ","hi"],["フ","fu"],["ヘ","he"],["ホ","ho"],
        ["マ","ma"],["ミ","mi"],["ム","mu"],["メ","me"],["モ","mo"],
        ["ヤ","ya"],["ユ","yu"],["ヨ","yo"],
        ["ラ","ra"],["リ","ri"],["ル","ru"],["レ","re"],["ロ","ro"],
        ["ワ","wa"],["ヲ","wo"],["ン","n"]
      ]},
      { label: "Dakuten (゛)", items: [
        ["ガ","ga"],["ギ","gi"],["グ","gu"],["ゲ","ge"],["ゴ","go"],
        ["ザ","za"],["ジ","ji"],["ズ","zu"],["ゼ","ze"],["ゾ","zo"],
        ["ダ","da"],["ヂ","ji"],["ヅ","zu"],["デ","de"],["ド","do"],
        ["バ","ba"],["ビ","bi"],["ブ","bu"],["ベ","be"],["ボ","bo"],
        ["パ","pa"],["ピ","pi"],["プ","pu"],["ペ","pe"],["ポ","po"]
      ]},
      { label: "Kết hợp (ヤ・ユ・ヨ)", items: [
        ["キャ","kya"],["キュ","kyu"],["キョ","kyo"],
        ["シャ","sha"],["シュ","shu"],["ショ","sho"],
        ["チャ","cha"],["チュ","chu"],["チョ","cho"],
        ["ニャ","nya"],["ニュ","nyu"],["ニョ","nyo"],
        ["ヒャ","hya"],["ヒュ","hyu"],["ヒョ","hyo"],
        ["ミャ","mya"],["ミュ","myu"],["ミョ","myo"],
        ["リャ","rya"],["リュ","ryu"],["リョ","ryo"],
        ["ギャ","gya"],["ギュ","gyu"],["ギョ","gyo"],
        ["ジャ","ja"],["ジュ","ju"],["ジョ","jo"],
        ["ビャ","bya"],["ビュ","byu"],["ビョ","byo"],
        ["ピャ","pya"],["ピュ","pyu"],["ピョ","pyo"]
      ]}
    ]
  }
};

// Từ vựng N5: [kanji/kana, romaji, nghĩa tiếng Việt, chủ đề]
const VOCAB = [
  // Số đếm
  ["一","ichi","một","Số đếm"],["二","ni","hai","Số đếm"],["三","san","ba","Số đếm"],
  ["四","yon/shi","bốn","Số đếm"],["五","go","năm","Số đếm"],["六","roku","sáu","Số đếm"],
  ["七","nana/shichi","bảy","Số đếm"],["八","hachi","tám","Số đếm"],["九","kyuu","chín","Số đếm"],
  ["十","juu","mười","Số đếm"],["百","hyaku","trăm","Số đếm"],["千","sen","nghìn","Số đếm"],
  // Ngày / Thời gian
  ["日","hi","ngày / mặt trời","Thời gian"],["月","tsuki","tháng / mặt trăng","Thời gian"],
  ["年","toshi","năm","Thời gian"],["時","toki","giờ","Thời gian"],["分","fun","phút","Thời gian"],
  ["今日","kyou","hôm nay","Thời gian"],["明日","ashita","ngày mai","Thời gian"],
  ["昨日","kinou","hôm qua","Thời gian"],["朝","asa","buổi sáng","Thời gian"],
  ["昼","hiru","buổi trưa","Thời gian"],["夜","yoru","buổi tối","Thời gian"],
  // Gia đình
  ["父","chichi","bố (nói về bố mình)","Gia đình"],["母","haha","mẹ (nói về mẹ mình)","Gia đình"],
  ["兄","ani","anh trai","Gia đình"],["姉","ane","chị gái","Gia đình"],
  ["弟","otouto","em trai","Gia đình"],["妹","imouto","em gái","Gia đình"],
  ["子供","kodomo","trẻ em / con","Gia đình"],["家族","kazoku","gia đình","Gia đình"],
  // Con người / Cơ thể
  ["人","hito","người","Con người"],["男","otoko","nam / đàn ông","Con người"],
  ["女","onna","nữ / phụ nữ","Con người"],["友達","tomodachi","bạn","Con người"],
  ["先生","sensei","giáo viên","Con người"],["学生","gakusei","học sinh / sinh viên","Con người"],
  ["目","me","mắt","Cơ thể"],["手","te","tay","Cơ thể"],["足","ashi","chân","Cơ thể"],
  ["口","kuchi","miệng","Cơ thể"],["耳","mimi","tai","Cơ thể"],
  // Đồ ăn / Nước uống
  ["水","mizu","nước","Đồ ăn"],["お茶","ocha","trà","Đồ ăn"],["牛乳","gyuunyuu","sữa bò","Đồ ăn"],
  ["米","kome","gạo","Đồ ăn"],["パン","pan","bánh mì","Đồ ăn"],["卵","tamago","trứng","Đồ ăn"],
  ["魚","sakana","cá","Đồ ăn"],["肉","niku","thịt","Đồ ăn"],["野菜","yasai","rau","Đồ ăn"],
  ["果物","kudamono","hoa quả","Đồ ăn"],["りんご","ringo","táo","Đồ ăn"],
  ["バナナ","banana","chuối","Đồ ăn"],["ご飯","gohan","cơm / bữa ăn","Đồ ăn"],
  // Động vật
  ["犬","inu","chó","Động vật"],["猫","neko","mèo","Động vật"],["鳥","tori","chim","Động vật"],
  ["馬","uma","ngựa","Động vật"],["魚","sakana","cá","Động vật"],
  // Nơi chốn
  ["家","ie","nhà","Nơi chốn"],["学校","gakkou","trường học","Nơi chốn"],
  ["会社","kaisha","công ty","Nơi chốn"],["図書館","toshokan","thư viện","Nơi chốn"],
  ["病院","byouin","bệnh viện","Nơi chốn"],["駅","eki","ga tàu","Nơi chốn"],
  ["店","mise","cửa hàng","Nơi chốn"],["日本","nippon","Nhật Bản","Nơi chốn"],
  // Đồ vật
  ["本","hon","sách","Đồ vật"],["鉛筆","enpitsu","bút chì","Đồ vật"],["車","kuruma","xe hơi","Đồ vật"],
  ["時計","tokei","đồng hồ","Đồ vật"],["電話","denwa","điện thoại","Đồ vật"],
  ["ドア","doa","cửa","Đồ vật"],["窓","mado","cửa sổ","Đồ vật"],
  // Tính từ / Trạng thái
  ["大きい","ookii","to","Tính từ"],["小さい","chiisai","nhỏ","Tính từ"],
  ["新しい","atarashii","mới","Tính từ"],["古い","furui","cũ","Tính từ"],
  ["高い","takai","cao / đắt","Tính từ"],["安い","yasui","rẻ","Tính từ"],
  ["良い","ii","tốt","Tính từ"],["悪い","warui","xấu / tệ","Tính từ"],
  ["暑い","atsui","(trời) nóng","Tính từ"],["寒い","samui","(trời) lạnh","Tính từ"],
  ["美味しい","oishii","ngon","Tính từ"],["楽しい","tanoshii","vui","Tính từ"],
  // Động từ
  ["行く","iku","đi","Động từ"],["来る","kuru","đến","Động từ"],["帰る","kaeru","về","Động từ"],
  ["食べる","taberu","ăn","Động từ"],["飲む","nomu","uống","Động từ"],["見る","miru","nhìn","Động từ"],
  ["聞く","kiku","nghe","Động từ"],["話す","hanasu","nói chuyện","Động từ"],
  ["読む","yomu","đọc","Động từ"],["書く","kaku","viết","Động từ"],["買う","kau","mua","Động từ"],
  ["する","suru","làm","Động từ"],["ある","aru","có (vật)","Động từ"],["いる","iru","có (người/động vật)","Động từ"],
  // Các từ khác
  ["これ","kore","cái này","Đại từ"],["それ","sore","cái đó","Đại từ"],["あれ","are","cái kia","Đại từ"],
  ["私","watashi","tôi","Đại từ"],["あなた","anata","bạn (ngôi 2)","Đại từ"],
  ["何","nani","cái gì","Nghi vấn"],["誰","dare","ai","Nghi vấn"],["どこ","doko","ở đâu","Nghi vấn"],
  ["いつ","itsu","khi nào","Nghi vấn"],["どう","dou","như thế nào","Nghi vấn"],
  ["はい","hai","vâng","Cảm thán"],["いいえ","iie","không","Cảm thán"],["ありがとう","arigatou","cảm ơn","Cảm thán"]
];

// Ngữ pháp N5: { pattern, meaning, example_jp, example_vn }
const GRAMMAR = [
  { pattern: "〜です", meaning: "Là ~ (thể lịch sự, thì hiện tại)", example_jp: "私は学生です。", example_vn: "Tôi là học sinh." },
  { pattern: "〜ではありません", meaning: "Không phải là ~ (phủ định lịch sự)", example_jp: "彼は先生ではありません。", example_vn: "Anh ấy không phải là giáo viên." },
  { pattern: "〜ました", meaning: "Đã ~ (quá khứ, thể lịch sự)", example_jp: "昨日、映画を見ました。", example_vn: "Hôm qua tôi đã xem phim." },
  { pattern: "〜ませんでした", meaning: "Đã không ~ (quá khứ phủ định)", example_jp: "行きませんでした。", example_vn: "Tôi đã không đi." },
  { pattern: "を + 食べる/飲む", meaning: "Trợ từ を đánh dấu tân ngữ trực tiếp", example_jp: "りんごを食べます。", example_vn: "Tôi ăn táo." },
  { pattern: "に + 行く/来る", meaning: "Trợ từ に chỉ đích đến / mục đích", example_jp: "学校に行きます。", example_vn: "Tôi đi đến trường." },
  { pattern: "で + động từ", meaning: "Trợ từ で chỉ nơi xảy ra hành động", example_jp: "図書館で本を読みます。", example_vn: "Tôi đọc sách ở thư viện." },
  { pattern: "の", meaning: "Trợ từ の nối sở hữu (A の B = B của A)", example_jp: "私の本", example_vn: "Quyển sách của tôi." },
  { pattern: "が", meaning: "Trợ từ が đánh dấu chủ ngữ / năng lực", example_jp: "猫がいます。", example_vn: "Có con mèo." },
  { pattern: "〜たい", meaning: "Muốn làm ~ (nguyện vọng)", example_jp: "水が飲みたいです。", example_vn: "Tôi muốn uống nước." },
  { pattern: "〜ています", meaning: "Đang ~ (tiến trình) / trạng thái tiếp diễn", example_jp: "本を読んでいます。", example_vn: "Tôi đang đọc sách." },
  { pattern: "〜ことができる", meaning: "Có thể làm ~ (năng lực)", example_jp: "日本語が話せます。", example_vn: "Tôi có thể nói tiếng Nhật." },
  { pattern: "〜ので / 〜から", meaning: "Bởi vì ~ (nguyên nhân)", example_jp: "忙しいので、行きません。", example_vn: "Vì bận nên tôi không đi." },
  { pattern: "〜たり〜たりする", meaning: "Làm việc này việc kia (liệt kê)", example_jp: "休みに本を読んだり、映画を見たりします。", example_vn: "Ngày nghỉ tôi đọc sách, xem phim này nọ." },
  { pattern: "〜てください", meaning: "Hãy làm ~ (yêu cầu lịch sự)", example_jp: "ここに書いてください。", example_vn: "Hãy viết vào đây." }
];
