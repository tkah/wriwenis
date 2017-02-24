Wriwenis
=======
A chatbot I created for my Intro to AI course as an attempt to pass the Turing test. It uses Angular on the front-end and a [Flask](http://flask.pocoo.org/) back-end that should be ready to deploy to Heroku. The idea is that you're speaking to a cult member of "Our Eternal Wriwenis" who gradually collects information about you (none of it saved beyond that session) in an attempt to get you to join his/her cult. It also uses Markov Chains, via [Markovify](https://github.com/jsvine/markovify), derived from a text comprised of the Ramayana, quotes from the Dalai Lama, Buddhist teachings, Rumi poetry, Psalms, Shakespeare sonnets and more. The markov chains are, at times, seeded with parts of the user's input identified using [TextBlob](https://textblob.readthedocs.io/en/dev/). It is my first Flask application and, while it did manage to win our internal class contest, there are still some flaws.

Markov generated sentences are tweeted to the [@wriwenis](https://twitter.com/wriwenis) Twitter account.

Demo
----
[Acolytes of Our Eternal Wriwenis](http://torrankaleke.com/wriwenis/#/home/)

Running
--------
To install dependencies, navigate to project directory and run
```
npm install
```

The back-end is built using Python 3. You might consider using a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/). Regardless of whether you do or not, to install the back-end dependencies, run
```
pip install -r requirements.txt
```
and then start the server with
```
python app.py
```

Building
--------
[Jade](https://www.npmjs.com/package/jade) and [SASS](http://sass-lang.com/) were used to build up the HTML and CSS respectively. Changes to files in __src/js__, __src/jade__ and __src/sass__ can be compiled with tasks in gulpfile.js ([Gulp](http://gulpjs.com/)).
