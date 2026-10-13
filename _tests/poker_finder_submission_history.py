"""Restore only the reviewed Poker finder event block and cache version."""

SCRIPT='assets/poker-finder.js'
PAGE='poker/find/index.html'
OLD_SHA='13dad324550b31b81fbb8ef79e1a32a608cde10f66ddd3b94f155d64af405a4b'
NEW_SHA='c8ad7e80e8f0d9be0a13421c2f2c45beb6744e6f447a70a08ea36c83628df987'
OLD="""  input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(update, 120); });
  input.addEventListener('search', () => update());
  input.addEventListener('keydown', event => {
    if (event.key === 'Enter') { event.preventDefault(); update(); heading.focus(); }
    if (event.key === 'Escape') { event.preventDefault(); clear(); }
  });
"""
NEW="""  function submit() {
    clearTimeout(timer); update(); heading.focus({preventScroll: true});
    heading.scrollIntoView({block: 'center', behavior: 'instant'});
  }
  input.addEventListener('input', event => { clearTimeout(timer); if (!event.isComposing) timer = setTimeout(update, 120); });
  input.addEventListener('compositionstart', () => clearTimeout(timer));
  input.addEventListener('compositionend', update);
  input.addEventListener('search', () => { clearTimeout(timer); update(); });
  input.addEventListener('keydown', event => {
    if (event.isComposing || event.keyCode === 229) return;
    if (event.key === 'Enter') { event.preventDefault(); submit(); }
    if (event.key === 'Escape') { event.preventDefault(); clear(); }
  });
"""


def before(path,data):
    path=str(path)
    if path not in {SCRIPT,PAGE}:return data
    binary=isinstance(data,bytes);text=data.decode() if binary else data
    if path==SCRIPT:text=text.replace(NEW,OLD,1)
    else:text=text.replace('/assets/poker-finder.js?v='+NEW_SHA[:12],
                           '/assets/poker-finder.js?v='+OLD_SHA[:12],1)
    return text.encode() if binary else text
