from flask import Flask, render_template, request
import pickle
import numpy as np

# Load models
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_score = pickle.load(open('similarity_score.pkl', 'rb'))

pt.index = pt.index.str.strip().str.lower()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
        book_name=list(popular_df['Book-Title'].values),
        author=list(popular_df['Book-Author'].values),
        image=list(popular_df['Image-URL-M'].values),
        votes=list(popular_df['num_ratings'].values),
        ratings=list(popular_df['avg_ratings'].values)
    )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html', pt_titles=pt.index.tolist())

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    if user_input:
        user_input = user_input.strip().lower()
    else:
        return render_template('recommend.html', data=[], pt_titles=pt.index.tolist())

    if user_input not in pt.index:
        return render_template('recommend.html', data=[], pt_titles=pt.index.tolist())

    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(
        list(enumerate(similarity_score[index])),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    data = []
    for i in similar_items:
        item = []
        book_title = pt.index[i[0]]
        temp_df = books[books['Book-Title'].str.strip().str.lower() == book_title]
        temp_df = temp_df.drop_duplicates('Book-Title')
        item.extend(list(temp_df['Book-Title'].values))
        item.extend(list(temp_df['Book-Author'].values))
        item.extend(list(temp_df['Image-URL-M'].values))
        data.append(item)

    return render_template('recommend.html', data=data, pt_titles=pt.index.tolist())

if __name__ == '__main__':
    app.run(debug=True)
