"""Public catalogue accounting, derived without new freshness claims."""
from collections import Counter
from html import escape

def supplement(resources):
    methods = Counter(e['review_method'] for e in resources)
    dates = Counter(e['reviewed_on'] for e in resources)
    categories = Counter(e['category'] for e in resources)
    limited = sorted((e for e in resources if e['review_method'] == 'index'), key=lambda e: e['title'])
    summary = (f"{len(resources)} unique resource destinations: {methods['page']} public-page reviews and "
               f"{methods['index']} search-index-only records. These describe review methods, not product quality scores.")
    date_rows = ''.join('<tr><th scope="row">'+escape(d)+'</th><td>'+str(n)+'</td></tr>' for d,n in sorted(dates.items(),reverse=True))
    limit_rows = ''.join('<li><a href="/poker/resources/#resource-'+e['id']+'">'+escape(e['title'])+'</a>: '+escape(e['notes'])+'</li>' for e in limited)
    return {'poker_review_summary':summary,'poker_review_dates':'<table class="viewer-table"><caption>Individual catalogue review dates, not a site-wide recheck</caption><thead><tr><th scope="col">Recorded date</th><th scope="col">Listings</th></tr></thead><tbody>'+date_rows+'</tbody></table>',
            'poker_review_limits':'<ul>'+limit_rows+'</ul>' if limited else '<p>No index-only records in this catalogue snapshot.</p>'}
