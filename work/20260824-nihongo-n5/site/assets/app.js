
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
