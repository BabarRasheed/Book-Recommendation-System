from flask import Flask, render_template, request
import pickle
import pandas as pd
import numpy as np


try:
    popular_df = pickle.load(open('popular.pkl', 'rb'))
    pt = pickle.load(open('pt.pkl', 'rb'))
    books = pickle.load(open('books.pkl', 'rb'))
    similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))
except Exception as e:
    print("An error occurred while loading pickle files:", e)

app = Flask(__name__)

# Normalize book titles to lowercase for case-insensitive matching
books['Book-Title-Lower'] = books['Book-Title'].str.lower()
pt.index = pt.index.str.lower()

# Round the avg_rating to one decimal place
popular_df['avg_rating'] = popular_df['avg_rating'].round(1)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name=popular_df['Book-Title'].tolist(),
                           author=popular_df["Book-Author"].tolist(),
                           image=popular_df['Image-URL-M'].tolist(),
                           votes=popular_df['num_ratings'].tolist(),
                           rating=popular_df['avg_rating'].tolist(),
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input').strip().lower()  # Normalize user input to lowercase

    # Check if the user input exists in the pivot table index
    if user_input not in pt.index:
        return render_template('recommend.html', error='Book not found.')

    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[:4]

    data = []

    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title-Lower'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        
        # Fetch avg_rating and num_ratings for the recommended book, if available
        filtered_df = popular_df[popular_df['Book-Title'].str.lower() == pt.index[i[0]]]
        if not filtered_df.empty:
            avg_rating = filtered_df['avg_rating'].values[0]
            num_ratings = filtered_df['num_ratings'].values[0]
        else:
            avg_rating = 'N/A'
            num_ratings = 'N/A'
        
        item.append(avg_rating)
        item.append(num_ratings)
        
        data.append(item)
    
    return render_template('recommend.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
