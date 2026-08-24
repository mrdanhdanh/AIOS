// N5 learning content data (offline, no external deps)
// All content is static and self-contained.

const N5_DATA = {
  hiragana: {
    title: "Hiragana (ひらがな)",
    desc: "Bảng chữ cái cơ bản dùng cho từ thuần Nhật và ngữ pháp. Có 46 ký tự gốc.",
    groups: [
      {
        label: "Cơ bản (Gojūon)",
        items: [
          { jp: "あ", roma: "a" }, { jp: "い", roma: "i" }, { jp: "う", roma: "u" }, { jp: "え", roma: "e" }, { jp: "お", roma: "o" },
          { jp: "か", roma: "ka" }, { jp: "き", roma: "ki" }, { jp: "く", roma: "ku" }, { jp: "け", roma: "ke" }, { jp: "こ", roma: "ko" },
          { jp: "さ", roma: "sa" }, { jp: "し", roma: "shi" }, { jp: "す", roma: "su" }, { jp: "せ", roma: "se" }, { jp: "そ", roma: "so" },
          { jp: "た", roma: "ta" }, { jp: "ち", roma: "chi" }, { jp: "つ", roma: "tsu" }, { jp: "て", roma: "te" }, { jp: "と", roma: "to" },
          { jp: "な", roma: "na" }, { jp: "に", roma: "ni" }, { jp: "ぬ", roma: "nu" }, { jp: "ね", roma: "ne" }, { jp: "の", roma: "no" },
          { jp: "は", roma: "ha" }, { jp: "ひ", roma: "hi" }, { jp: "ふ", roma: "fu" }, { jp: "へ", roma: "he" }, { jp: "ほ", roma: "ho" },
          { jp: "ま", roma: "ma" }, { jp: "み", roma: "mi" }, { jp: "む", roma: "mu" }, { jp: "め", roma: "me" }, { jp: "も", roma: "mo" },
          { jp: "や", roma: "ya" }, { jp: "ゆ", roma: "yu" }, { jp: "よ", roma: "yo" },
          { jp: "ら", roma: "ra" }, { jp: "り", roma: "ri" }, { jp: "る", roma: "ru" }, { jp: "れ", roma: "re" }, { jp: "ろ", roma: "ro" },
          { jp: "わ", roma: "wa" }, { jp: "を", roma: "wo" }, { jp: "ん", roma: "n" }
        ]
      },
      {
        label: "Dakuten (゛) & Handakuten (゜)",
        items: [
          { jp: "が", roma: "ga" }, { jp: "ぎ", roma: "gi" }, { jp: "ぐ", roma: "gu" }, { jp: "げ", roma: "ge" }, { jp: "ご", roma: "go" },
          { jp: "ざ", roma: "za" }, { jp: "じ", roma: "ji" }, { jp: "ず", roma: "zu" }, { jp: "ぜ", roma: "ze" }, { jp: "ぞ", roma: "zo" },
          { jp: "だ", roma: "da" }, { jp: "ぢ", roma: "ji" }, { jp: "づ", roma: "zu" }, { jp: "で", roma: "de" }, { jp: "ど", roma: "do" },
          { jp: "ば", roma: "ba" }, { jp: "び", roma: "bi" }, { jp: "ぶ", roma: "bu" }, { jp: "べ", roma: "be" }, { jp: "ぼ", roma: "bo" },
          { jp: "ぱ", roma: "pa" }, { jp: "ぴ", roma: "pi" }, { jp: "ぷ", roma: "pu" }, { jp: "ぺ", roma: "pe" }, { jp: "ぽ", roma: "po" }
        ]
      },
      {
        label: "Ký tự ghép (Yōon)",
        items: [
          { jp: "きゃ", roma: "kya" }, { jp: "きゅ", roma: "kyu" }, { jp: "きょ", roma: "kyo" },
          { jp: "しゃ", roma: "sha" }, { jp: "しゅ", roma: "shu" }, { jp: "しょ", roma: "sho" },
          { jp: "ちゃ", roma: "cha" }, { jp: "ちゅ", roma: "chu" }, { jp: "ちょ", roma: "cho" },
          { jp: "にゃ", roma: "nya" }, { jp: "にゅ", roma: "nyu" }, { jp: "にょ", roma: "nyo" },
          { jp: "ひゃ", roma: "hya" }, { jp: "ひゅ", roma: "hyu" }, { jp: "ひょ", roma: "hyo" },
          { jp: "みゃ", roma: "mya" }, { jp: "みゅ", roma: "myu" }, { jp: "みょ", roma: "myo" },
          { jp: "りゃ", roma: "rya" }, { jp: "りゅ", roma: "ryu" }, { jp: "りょ", roma: "ryo" },
          { jp: "ぎゃ", roma: "gya" }, { jp: "ぎゅ", roma: "gyu" }, { jp: "ぎょ", roma: "gyo" },
          { jp: "じゃ", roma: "ja" }, { jp: "じゅ", roma: "ju" }, { jp: "じょ", roma: "jo" },
          { jp: "びゃ", roma: "bya" }, { jp: "びゅ", roma: "byu" }, { jp: "びょ", roma: "byo" },
          { jp: "ぴゃ", roma: "pya" }, { jp: "ぴゅ", roma: "pyu" }, { jp: "ぴょ", roma: "pyo" }
        ]
      }
    ]
  },

  katakana: {
    title: "Katakana (カタカナ)",
    desc: "Dùng cho từ mượn nước ngoài, tên riêng, và onomatopoeia. Cấu trúc giống hiragana.",
    groups: [
      {
        label: "Cơ bản (Gojūon)",
        items: [
          { jp: "ア", roma: "a" }, { jp: "イ", roma: "i" }, { jp: "ウ", roma: "u" }, { jp: "エ", roma: "e" }, { jp: "オ", roma: "o" },
          { jp: "カ", roma: "ka" }, { jp: "キ", roma: "ki" }, { jp: "ク", roma: "ku" }, { jp: "ケ", roma: "ke" }, { jp: "コ", roma: "ko" },
          { jp: "サ", roma: "sa" }, { jp: "シ", roma: "shi" }, { jp: "ス", roma: "su" }, { jp: "セ", roma: "se" }, { jp: "ソ", roma: "so" },
          { jp: "タ", roma: "ta" }, { jp: "チ", roma: "chi" }, { jp: "ツ", roma: "tsu" }, { jp: "テ", roma: "te" }, { jp: "ト", roma: "to" },
          { jp: "ナ", roma: "na" }, { jp: "ニ", roma: "ni" }, { jp: "ヌ", roma: "nu" }, { jp: "ネ", roma: "ne" }, { jp: "ノ", roma: "no" },
          { jp: "ハ", roma: "ha" }, { jp: "ヒ", roma: "hi" }, { jp: "フ", roma: "fu" }, { jp: "ヘ", roma: "he" }, { jp: "ホ", roma: "ho" },
          { jp: "マ", roma: "ma" }, { jp: "ミ", roma: "mi" }, { jp: "ム", roma: "mu" }, { jp: "メ", roma: "me" }, { jp: "モ", roma: "mo" },
          { jp: "ヤ", roma: "ya" }, { jp: "ユ", roma: "yu" }, { jp: "ヨ", roma: "yo" },
          { jp: "ラ", roma: "ra" }, { jp: "リ", roma: "ri" }, { jp: "ル", roma: "ru" }, { jp: "レ", roma: "re" }, { jp: "ロ", roma: "ro" },
          { jp: "ワ", roma: "wa" }, { jp: "ヲ", roma: "wo" }, { jp: "ン", roma: "n" }
        ]
      },
      {
        label: "Dakuten (゛) & Handakuten (゜)",
        items: [
          { jp: "ガ", roma: "ga" }, { jp: "ギ", roma: "gi" }, { jp: "グ", roma: "gu" }, { jp: "ゲ", roma: "ge" }, { jp: "ゴ", roma: "go" },
          { jp: "ザ", roma: "za" }, { jp: "ジ", roma: "ji" }, { jp: "ズ", roma: "zu" }, { jp: "ゼ", roma: "ze" }, { jp: "ゾ", roma: "zo" },
          { jp: "ダ", roma: "da" }, { jp: "ヂ", roma: "ji" }, { jp: "ヅ", roma: "zu" }, { jp: "デ", roma: "de" }, { jp: "ド", roma: "do" },
          { jp: "バ", roma: "ba" }, { jp: "ビ", roma: "bi" }, { jp: "ブ", roma: "bu" }, { jp: "ベ", roma: "be" }, { jp: "ボ", roma: "bo" },
          { jp: "パ", roma: "pa" }, { jp: "ピ", roma: "pi" }, { jp: "プ", roma: "pu" }, { jp: "ペ", roma: "pe" }, { jp: "ポ", roma: "po" }
        ]
      },
      {
        label: "Ký tự ghép (Yōon)",
        items: [
          { jp: "キャ", roma: "kya" }, { jp: "キュ", roma: "kyu" }, { jp: "キョ", roma: "kyo" },
          { jp: "シャ", roma: "sha" }, { jp: "シュ", roma: "shu" }, { jp: "ショ", roma: "sho" },
          { jp: "チャ", roma: "cha" }, { jp: "チュ", roma: "chu" }, { jp: "チョ", roma: "cho" },
          { jp: "ニャ", roma: "nya" }, { jp: "ニュ", roma: "nyu" }, { jp: "ニョ", roma: "nyo" },
          { jp: "ヒャ", roma: "hya" }, { jp: "ヒュ", roma: "hyu" }, { jp: "ヒョ", roma: "hyo" },
          { jp: "ミャ", roma: "mya" }, { jp: "ミュ", roma: "myu" }, { jp: "ミョ", roma: "myo" },
          { jp: "リャ", roma: "rya" }, { jp: "リュ", roma: "ryu" }, { jp: "リョ", roma: "ryo" },
          { jp: "ギャ", roma: "gya" }, { jp: "ギュ", roma: "gyu" }, { jp: "ギョ", roma: "gyo" },
          { jp: "ジャ", roma: "ja" }, { jp: "ジュ", roma: "ju" }, { jp: "ジョ", roma: "jo" },
          { jp: "ビャ", roma: "bya" }, { jp: "ビュ", roma: "byu" }, { jp: "ビョ", roma: "byo" },
          { jp: "ピャ", roma: "pya" }, { jp: "ピュ", roma: "pyu" }, { jp: "ピョ", roma: "pyo" }
        ]
      }
    ]
  },

  greetings: {
    title: "Chào hỏi & Giao tiếp (あいさつ)",
    desc: "Những câu giao tiếp cơ bản nhất trong đời sống hàng ngày.",
    items: [
      { jp: "こんにちは", roma: "Konnichiwa", vi: "Xin chào (ban ngày)" },
      { jp: "おはようございます", roma: "Ohayou gozaimasu", vi: "Chào buổi sáng" },
      { jp: "こんばんは", roma: "Konbanwa", vi: "Chào buổi tối" },
      { jp: "さようなら", roma: "Sayounara", vi: "Tạm biệt" },
      { jp: "ありがとうございます", roma: "Arigatou gozaimasu", vi: "Cảm ơn bạn" },
      { jp: "すみません", roma: "Sumimasen", vi: "Xin lỗi / Làm ơn" },
      { jp: "はじめまして", roma: "Hajimemashite", vi: "Rất hân hạnh được gặp bạn" },
      { jp: "おねがいします", roma: "Onegaishimasu", vi: "Làm ơn / Xin hãy" },
      { jp: "はい", roma: "Hai", vi: "Vâng / Đúng" },
      { jp: "いいえ", roma: "Iie", vi: "Không" },
      { jp: "おやすみなさい", roma: "Oyasuminasai", vi: "Chúc ngủ ngon" },
      { jp: "いただきます", roma: "Itadakimasu", vi: "(Nói trước khi ăn)" },
      { jp: "ごちそうさま", roma: "Gochisousama", vi: "(Nói sau khi ăn xong)" },
      { jp: "げんきですか", roma: "Genki desu ka", vi: "Bạn khỏe không?" }
    ]
  },

  numbers: {
    title: "Số đếm (すうじ)",
    desc: "Số từ 0 đến 10, cùng các số chục, trăm, nghìn. Lưu ý 4 và 7 có 2 cách đọc.",
    items: [
      { jp: "0", roma: "zero / rei", vi: "Số không" },
      { jp: "1", roma: "ichi", vi: "Một" },
      { jp: "2", roma: "ni", vi: "Hai" },
      { jp: "3", roma: "san", vi: "Ba" },
      { jp: "4", roma: "shi / yon", vi: "Bốn" },
      { jp: "5", roma: "go", vi: "Năm" },
      { jp: "6", roma: "roku", vi: "Sáu" },
      { jp: "7", roma: "shichi / nana", vi: "Bảy" },
      { jp: "8", roma: "hachi", vi: "Tám" },
      { jp: "9", roma: "ku / kyuu", vi: "Chín" },
      { jp: "10", roma: "juu", vi: "Mười" },
      { jp: "20", roma: "nijuu", vi: "Hai mươi" },
      { jp: "100", roma: "hyaku", vi: "Một trăm" },
      { jp: "1000", roma: "sen", vi: "Một nghìn" },
      { jp: "10000", roma: "man", vi: "Một vạn (10 nghìn)" }
    ]
  },

  vocabulary: {
    title: "Từ vựng theo chủ đề (ことば)",
    desc: "Từ vựng N5 phân theo nhóm để dễ học và ôn tập.",
    groups: [
      {
        label: "Màu sắc",
        items: [
          { jp: "あか", roma: "aka", vi: "Đỏ" },
          { jp: "あお", roma: "ao", vi: "Xanh (nước)" },
          { jp: "しろ", roma: "shiro", vi: "Trắng" },
          { jp: "くろ", roma: "kuro", vi: "Đen" },
          { jp: "きいろ", roma: "kiiro", vi: "Vàng" },
          { jp: "みどり", roma: "midori", vi: "Xanh (lá)" },
          { jp: "ちゃいろ", roma: "chairo", vi: "Nâu" }
        ]
      },
      {
        label: "Gia đình",
        items: [
          { jp: "ちち", roma: "chichi", vi: "Bố (nói khiêm tốn)" },
          { jp: "はは", roma: "haha", vi: "Mẹ (nói khiêm tốn)" },
          { jp: "あに", roma: "ani", vi: "Anh trai" },
          { jp: "あね", roma: "ane", vi: "Chị gái" },
          { jp: "おとうと", roma: "otouto", vi: "Em trai" },
          { jp: "いもうと", roma: "imouto", vi: "Em gái" },
          { jp: "おじいさん", roma: "ojiisan", vi: "Ông" },
          { jp: "おばあさん", roma: "obaasan", vi: "Bà" }
        ]
      },
      {
        label: "Đồ ăn & Đồ uống",
        items: [
          { jp: "ごはん", roma: "gohan", vi: "Cơm / Bữa ăn" },
          { jp: "さかな", roma: "sakana", vi: "Cá" },
          { jp: "にく", roma: "niku", vi: "Thịt" },
          { jp: "やさい", roma: "yasai", vi: "Rau" },
          { jp: "みず", roma: "mizu", vi: "Nước lọc" },
          { jp: "おちゃ", roma: "ocha", vi: "Trà" },
          { jp: "コーヒー", roma: "koohii", vi: "Cà phê" },
          { jp: "パン", roma: "pan", vi: "Bánh mì" }
        ]
      },
      {
        label: "Thời gian",
        items: [
          { jp: "いま", roma: "ima", vi: "Bây giờ" },
          { jp: "あさ", roma: "asa", vi: "Buổi sáng" },
          { jp: "ひる", roma: "hiru", vi: "Buổi trưa" },
          { jp: "ばん", roma: "ban", vi: "Buổi tối" },
          { jp: "よる", roma: "yoru", vi: "Đêm" },
          { jp: "きょう", roma: "kyou", vi: "Hôm nay" },
          { jp: "あした", roma: "ashita", vi: "Ngày mai" },
          { jp: "きのう", roma: "kinou", vi: "Hôm qua" }
        ]
      },
      {
        label: "Động từ thường gặp",
        items: [
          { jp: "いく", roma: "iku", vi: "Đi" },
          { jp: "くる", roma: "kuru", vi: "Đến" },
          { jp: "たべる", roma: "taberu", vi: "Ăn" },
          { jp: "のむ", roma: "nomu", vi: "Uống" },
          { jp: "する", roma: "suru", vi: "Làm" },
          { jp: "みる", roma: "miru", vi: "Xem / Nhìn" },
          { jp: "かう", roma: "kau", vi: "Mua" },
          { jp: "わかる", roma: "wakaru", vi: "Hiểu" }
        ]
      },
      {
        label: "Tính từ",
        items: [
          { jp: "おおきい", roma: "ookii", vi: "To / Lớn" },
          { jp: "ちいさい", roma: "chiisai", vi: "Nhỏ" },
          { jp: "あたらしい", roma: "atarashii", vi: "Mới" },
          { jp: "ふるい", roma: "furui", vi: "Cũ" },
          { jp: "いい / よい", roma: "ii / yoi", vi: "Tốt" },
          { jp: "わるい", roma: "warui", vi: "Xấu" }
        ]
      }
    ]
  },

  grammar: {
    title: "Ngữ pháp N5 (ぶんぽう)",
    desc: "10 điểm ngữ pháp cốt lõi nhất của trình độ N5.",
    items: [
      {
        jp: "〜は〜です",
        roma: "X wa Y desu",
        vi: "X là Y (khẳng định trạng thái). VD: わたしはがくせいです (Tôi là sinh viên).",
        note: "は đọc là 'wa' khi là trợ từ."
      },
      {
        jp: "〜を〜ます",
        roma: "X o Y masu",
        vi: "Đối tượng X + động từ Y (thể lịch sự). VD: ほんをよみます (Đọc sách).",
        note: "を (o) là trợ từ chỉ tân ngữ."
      },
      {
        jp: "〜に〜ます",
        roma: "X ni Y masu",
        vi: "Hướng tới X / thời điểm X + động từ. VD: にほんにいきます (Đi Nhật Bản).",
        note: "に (ni) chỉ đích đến hoặc thời điểm."
      },
      {
        jp: "〜が〜",
        roma: "X ga ...",
        vi: "X là chủ ngữ được nhấn mạnh / mới biết. VD: ねこがいます (Có con mèo).",
        note: "が (ga) nhấn mạnh chủ ngữ."
      },
      {
        jp: "い形容詞 / な形容詞 + です",
        roma: "Adj + desu",
        vi: "Tính từ + desu. い-adj giữ nguyên (たかいです), な-adj bỏ な (げんきです).",
        note: "Phủ định: たかくないです / げんきじゃないです."
      },
      {
        jp: "〜ています",
        roma: "te imasu",
        vi: "Đang làm ~ (thể tiếp diễn). VD: べんきょうしています (Đang học).",
        note: "Thêm います sau dạng て."
      },
      {
        jp: "〜たい",
        roma: "tai",
        vi: "Muốn làm ~. VD: いきたいです (Muốn đi).",
        note: "Chỉ dùng cho ý muốn của người nói."
      },
      {
        jp: "〜ませんか",
        roma: "masen ka",
        vi: "Mời / đề nghị làm ~ không? VD: いっしょにいきませんか (Đi cùng không?).",
        note: "Cách mời lịch sự."
      },
      {
        jp: "〜の",
        roma: "no",
        vi: "Của / giải thích. VD: わたしのほん (Sách của tôi).",
        note: "の (no) nối sở hữu."
      },
      {
        jp: "〜か (nghi vấn)",
        roma: "ka",
        vi: "Dấu hỏi. VD: がくせいですか (Là sinh viên phải không?).",
        note: "Cuối câu thành câu hỏi."
      }
    ]
  }
};

// Quiz pool: combine kana + vocab for multiple-choice practice
function buildQuizPool() {
  const pool = [];
  N5_DATA.hiragana.groups.forEach(g => g.items.forEach(it => pool.push({ q: it.jp, a: it.roma, cat: "Hiragana" })));
  N5_DATA.katakana.groups.forEach(g => g.items.forEach(it => pool.push({ q: it.jp, a: it.roma, cat: "Katakana" })));
  N5_DATA.vocabulary.groups.forEach(g => g.items.forEach(it => pool.push({ q: it.jp, a: it.roma, cat: "Từ vựng" })));
  N5_DATA.greetings.items.forEach(it => pool.push({ q: it.jp, a: it.roma, cat: "Chào hỏi" }));
  return pool;
}
