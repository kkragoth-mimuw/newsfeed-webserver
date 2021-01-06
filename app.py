import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from flask import Flask, render_template

app = Flask(__name__)

cred = credentials.Certificate('/opt/firebase/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

LIMIT_PER_PAGE = 5

@app.route('/', defaults={'page': 0})
@app.route('/news')
@app.route('/news/<page>')
def news(page=0):
    page = int(page)
    news = []

    news_ref = db.collection(u'news').order_by(
        u'timestamp', direction=firestore.Query.DESCENDING
        ).limit(LIMIT_PER_PAGE)

    cp_page = page
    while cp_page > 0:
        docs = list(news_ref.stream())
        if len(docs) == 0:
            break
        last_doc = docs[-1]

        last_timestamp = last_doc.to_dict()[u'timestamp']

        news_ref = db.collection(u'news').order_by(
            u'timestamp', direction=firestore.Query.DESCENDING
        ).start_after({
            u'timestamp': last_timestamp
        }).limit(LIMIT_PER_PAGE)

        cp_page -= 1

    news = list(map(lambda x: x.to_dict(), news_ref.stream()))

    return render_template('index.html', news=news, news_len=len(news), limit=LIMIT_PER_PAGE, page=page)


if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    print('starting')
    app.run(debug=False, port=server_port, host='0.0.0.0')