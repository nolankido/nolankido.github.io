/* A limited, deterministic rule rehearsal. No cards, strategy grades or saved state. */
(function () {
  'use strict';
  const LIMIT = 1000;
  const copy = s => ({...s, players:s.players.map(p=>({...p})), pending:[...s.pending], ending:s.ending ? {...s.ending} : null});
  function start(value) {
    if (!value || !['preflop','flop'].includes(value.street) || value.bigBlind !== 2 ||
        !['priorPot','current','lastRaise'].every(k=>Number.isInteger(value[k]) && value[k]>=0 && value[k]<=LIMIT) || value.lastRaise<2 ||
        !Array.isArray(value.players) || value.players.length!==3 || !Array.isArray(value.pending) || !value.pending.length) throw Error('Invalid starting round');
    const s = copy({...value,ending:null});
    if (s.players.some((p,i)=>p.id!==['button','small','big'][i] || typeof p.name!=='string' || !p.name.trim() || typeof p.folded!=='boolean' || !Number.isInteger(p.paid) || p.paid<0 || p.paid>LIMIT) ||
        s.current!==Math.max(...s.players.map(p=>p.paid)) || new Set(s.pending).size!==s.pending.length ||
        s.pending.some(id=>!s.players.some(p=>p.id===id && !p.folded)) || s.players.filter(p=>!p.folded).length<2 ||
        s.players.some(p=>!p.folded && p.paid<s.current && !s.pending.includes(p.id))) throw Error('Invalid starting decisions');
    return s;
  }
  const pot = s => s.priorPot + s.players.reduce((sum,p)=>sum+p.paid,0);
  function act(source, action, add) {
    const fail = (code,message) => ({ok:false,code,message,state:source});
    if (source.ending) return fail('closed','This round has ended. Restart it to try another line.');
    const s=copy(source), id=s.pending[0], p=s.players.find(x=>x.id===id), owed=s.current-p.paid;
    if (!['check','bet','call','raise','fold'].includes(action)) return fail('action','Choose an action first.');
    if (action==='check' && owed) return fail('check-facing',p.name+' owes '+owed+'. Checking cannot answer an unmatched wager. Choose fold, call or a full raise.');
    if (action==='call' && !owed) return fail('call-zero','Nothing is owed. Use check to pass without paying, or '+(s.current?'raise':'bet')+' to increase the wager.');
    if (action==='bet' && s.current) return fail('bet-existing','A wager already exists on this round. Increasing it is a raise. The preflop big blind counts as a live wager.');
    if (action==='raise' && !s.current) return fail('raise-none','No wager has opened this round. Use bet to open it, or check to pass.');
    if (action==='fold' && !owed) return fail('fold-free','Nothing is owed. Use check to keep the hand for free in this exercise. A fold without facing a wager can be binding and penalized in live tournament play.');
    if (!Number.isInteger(add) || add<0 || add>LIMIT || (['check','fold'].includes(action) && add!==0)) return fail('amount','Enter whole counters to add, from 0 to 1,000. Check and fold add zero.');
    if (action==='call' && add!==owed) return fail('call-cost','A call adds '+s.current+' minus '+p.paid+' = '+owed+'. The input is extra counters, not the total wager.');
    const target=p.paid+add;
    if (action==='bet' && add<s.bigBlind) return fail('minimum','Here the minimum opening bet is '+s.bigBlind+', the big blind. Short all-ins are outside this exercise.');
    if (action==='raise' && target<s.current+s.lastRaise) return fail('minimum','The last full bet or raise increased the wager by '+s.lastRaise+'. Reach at least '+(s.current+s.lastRaise)+' total: add at least '+(s.current+s.lastRaise-p.paid)+' to this seat’s '+p.paid+'.');
    if (target>LIMIT) return fail('ceiling','Keep this seat’s round total at or below 1,000 in this rehearsal. This practice ceiling is not a poker rule.');
    s.pending.shift();
    if (action==='fold') p.folded=true;
    else p.paid=target;
    if (action==='bet' || action==='raise') {
      s.lastRaise=target-s.current; s.current=target;
      const i=s.players.findIndex(x=>x.id===id);
      s.pending=[1,2].map(n=>s.players[(i+n)%3]).filter(x=>!x.folded).map(x=>x.id);
    }
    const remaining=s.players.filter(x=>!x.folded);
    if (remaining.length===1) {
      const winner=remaining[0], other=Math.max(...s.players.filter(x=>x.id!==winner.id).map(x=>x.paid));
      const returned=Math.max(0,winner.paid-other);
      s.pending=[]; s.ending={kind:'fold',winner:winner.id,returned,awarded:pot(s)-returned};
    } else if (!s.pending.length) {
      s.ending={kind:'round',next:s.street==='preflop'?'flop':'turn',pot:pot(s)};
    }
    return {ok:true,state:s,actor:id,action,add};
  }
  if (typeof module!=='undefined' && module.exports) module.exports={start,act,pot};
  if (typeof document==='undefined') return;
  const root=document.querySelector('[data-round-practice]');
  if (!root) return;
  const articles=[...root.querySelectorAll('[data-round-case]')];
  let states;
  try {
    if (articles.length!==3 || articles.some((n,i)=>n.id!=='round-practice-'+['preflop','flop','raise'][i] || !n.querySelector('h3') || !n.querySelector('[data-round-live]') || !n.querySelector('[data-round-native]') || !n.querySelector('[data-round-worked]'))) return;
    states=articles.map(n=>start(JSON.parse(n.dataset.roundState)));
  } catch (_) { return; }
  const make=(tag,text,cls)=>{const n=document.createElement(tag);if(text)n.textContent=text;if(cls)n.className=cls;return n;};
  const reveal = node => { node.focus({preventScroll:true}); node.scrollIntoView({block:'start',behavior:'instant'}); };
  const rules={
    'check-facing':['Actions facing a wager','legal-actions'], 'call-zero':['Checking when nothing is owed','legal-actions'],
    'bet-existing':['Bet versus raise','legal-actions'], 'raise-none':['Bet versus raise','legal-actions'], 'fold-free':['Check versus fold','legal-actions'],
    'call-cost':['Additional call counters','chips-owed'], minimum:['The last full raise increment','check-min-raise']
  };
  articles.forEach((article,i)=>{
    let state=states[i];
    const notes=new Set(), live=article.querySelector('[data-round-live]');
    const turn=make('h4','', 'round-turn');turn.tabIndex=-1;turn.dataset.roundTurn='';
    const totals=make('p','', 'round-totals');totals.dataset.roundTotals='';
    const area=make('div');
    const choices=make('fieldset'), legend=make('legend','Choose a move for the next seat');choices.append(legend);
    const label=make('label','Action');label.htmlFor=article.id+'-action';
    const action=make('select');action.id=label.htmlFor;action.dataset.roundAction='';
    [['','Choose an action'],['check','Check'],['bet','Bet'],['call','Call'],['raise','Raise'],['fold','Fold']].forEach(([v,t])=>{const o=make('option',t);o.value=v;action.append(o);});
    label.append(action);
    const addLabel=make('label','Counters to add now');addLabel.htmlFor=article.id+'-amount';
    const amount=make('input');amount.type='text';amount.inputMode='numeric';amount.autocomplete='off';amount.id=addLabel.htmlFor;amount.dataset.roundAmount='';amount.disabled=true;amount.setAttribute('aria-describedby',article.id+'-amount-help');
    addLabel.append(amount);
    const help=make('p','For a call, bet or raise, enter extra counters for this seat on this round. Check and fold add zero. This rehearsal checks the move before applying it; venue rulings for mistaken declarations are outside the model.','round-input-help');help.id=article.id+'-amount-help';
    const submit=make('button','Try this move');submit.type='button';submit.dataset.roundMove='';
    choices.append(label,addLabel,help,submit);
    const status=make('p','', 'round-feedback');status.setAttribute('role','status');status.setAttribute('aria-live','polite');status.dataset.roundFeedback='';status.tabIndex=-1;
    const logDetail=make('details','', 'poker-details');const logSummary=make('summary','Your line so far');const log=make('ol');log.dataset.roundLog='';logDetail.append(logSummary,log);
    const restart=make('button','Restart this round');restart.type='button';restart.dataset.roundRestart='';
    const review=make('div','', 'round-review');review.dataset.roundReview='';
    live.append(turn,totals,area,status,choices,logDetail,restart,review);
    function showReview() {
      review.replaceChildren();
      if (!notes.size) return;
      review.append(make('p','Rules to revisit from this visit. Corrections stay here after a successful retry or restart; these are study notes, not a score.'));
      const ul=make('ul');
      notes.forEach(code=>{const li=make('li');if(code==='worked')li.textContent='Used the worked line. Try the same idea again later without the example.';else {const a=make('a',rules[code][0]);a.href='/poker/first-decisions/#'+rules[code][1];li.append(a);}ul.append(li);});review.append(ul);
    }
    function render() {
      const table=make('table','', 'viewer-table round-table');table.append(make('caption','Payments on this betting round'));
      const head=make('thead'), hr=make('tr');['Seat','Paid this round','Status'].forEach(t=>{const th=make('th',t);th.scope='col';hr.append(th);});head.append(hr);
      const body=make('tbody');
      state.players.forEach(p=>{const row=make('tr'), name=make('th',p.name);name.scope='row';const current=!state.ending && p.id===state.pending[0];row.append(name,make('td',String(p.paid)),make('td',p.folded?'Folded':current?'Next to act':'In the hand'));if(current)row.className='round-current';body.append(row);});table.append(head,body);area.replaceChildren(table);
      const p=state.players.find(x=>x.id===state.pending[0]);
      totals.textContent=(state.ending?'Pot before settlement: ':'Pot now: ')+pot(state)+'. Total wager on this round: '+state.current+'. Earlier-round pot: '+state.priorPot+'.';
      if (!state.ending) turn.textContent=p.name+' acts next. Say why before choosing a move.';
      else if (state.ending.kind==='round') turn.textContent='Round finished. The '+state.ending.next+' can be dealt. Everyone remaining has responded to the latest wager.';
      else {const end=state.ending,winner=state.players.find(x=>x.id===end.winner);turn.textContent='Hand finished. '+winner.name+' is the only player left. Return '+end.returned+' uncalled '+(end.returned===1?'counter':'counters')+', then award the remaining pot of '+end.awarded+'. No showdown is needed.';}
      choices.hidden=!!state.ending;
    }
    function attempt() {
      let add=0;
      if (['call','bet','raise'].includes(action.value)) add=/^[0-9]+$/.test(amount.value.trim())?Number(amount.value.trim()):NaN;
      const r=act(state,action.value,add);
      if (!r.ok) {status.textContent=r.message;if(rules[r.code]){notes.add(r.code);showReview();}amount.setAttribute('aria-invalid',['amount','call-cost','minimum','ceiling'].includes(r.code)?'true':'false');reveal(status);return;}
      const player=state.players.find(p=>p.id===r.actor);state=r.state;
      const words=player.name+': '+r.action+(r.add?'; added '+r.add+', now paid '+state.players.find(p=>p.id===r.actor).paid+' this round':'')+'.';
      log.append(make('li',words));logDetail.open=true;status.textContent=words+' This move follows the rules in the model.';
      action.value='';amount.value='';amount.disabled=true;amount.removeAttribute('aria-invalid');render();reveal(turn);
    }
    submit.addEventListener('click',attempt);
    amount.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();attempt();}});
    action.addEventListener('change',()=>{amount.disabled=!['call','bet','raise'].includes(action.value);amount.value='';amount.removeAttribute('aria-invalid');status.textContent='';});
    restart.addEventListener('click',()=>{state=start(states[i]);action.value='';amount.value='';amount.disabled=true;amount.removeAttribute('aria-invalid');log.replaceChildren();status.textContent='Round restarted. Try a different line, or repeat without the worked example.';render();reveal(turn);});
    article.querySelector('[data-round-worked]').addEventListener('toggle',e=>{if(e.target.open){notes.add('worked');showReview();}});
    render();live.hidden=false;article.querySelector('[data-round-native]').hidden=true;
  });
  function activate(id,focus) {
    const chosen=articles.find(n=>n.id===id || n.id+'-title'===id);
    if (!chosen) return;
    articles.forEach(n=>{n.hidden=n!==chosen;});
    if (focus) document.fonts.ready.then(()=>requestAnimationFrame(()=>{if(location.hash.slice(1)===id) reveal(chosen.querySelector('h3'));}));
  }
  root.classList.add('round-enhanced');
  activate(location.hash.slice(1),false);
  if (!articles.some(n=>n.hidden)) activate(articles[0].id,false);
  function followFragment() {
    const id=location.hash.slice(1);
    if(id==='betting-rehearsal') document.fonts.ready.then(()=>requestAnimationFrame(()=>{if(location.hash.slice(1)===id)reveal(root.querySelector('h2'));}));
    else activate(id,true);
  }
  followFragment();
  window.addEventListener('hashchange',followFragment);
  root.querySelectorAll('.round-starts a').forEach(a=>a.addEventListener('click',()=>activate(a.hash.slice(1),true)));
}());
