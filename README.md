# A simple REST API exercise.

REST API implemented using the minimal veneer of Restless.

Tests are present for basic things. Many more tests can be written,
e.g. to demonstrate proper error handling.

## How to use

    pip install < requirements.txt
    cd letterpush
    ./manage.py migrate
    ./manage.py test rest_api.resources_tests

Then play around using e.g. HTTPie. No auth required.

    ./manage.py runserver
    echo '{"path": "lolcat.jpg", "note": "They love cats"}' | http POST localhost:8000/api/images/
    echo '{"title: "Cats!", "body": "Just look."}' | http POST localhost:8000/api/articles/
    # Note the article and image IDs above.
    echo '{"image_id": 1, "article_id": 1, "role": "L"}' | http POST localhost:8000/api/image_links/
    http GET localhost:8000/api/articles/
    echo '{"body": "Updated news about cats"}' | http PUT localhost:8000/api/articles/1/

Etc.


## Why so late??

Took quite a bit longer, not because of the time required,
but mostly to carve produictive time from home life.

It took around 6 hours rahter than 4, but from the commit history
the actual velocity can be seen.
