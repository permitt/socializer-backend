# The Socializer - Backend

# Demo Video

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/0JVTitsQ9MA/0.jpg)](https://www.youtube.com/watch?v=0JVTitsQ9MA)

# About
Web Application built in <b>Django & React</b>. <br>
Users can add their Instagram Account and then select their friends to follow their posts/stories. <br>
Users have an option to receive an email whenever their friend posts a story/post.<br>
Every story/post is processed through a deep learning image captioning model to generate a caption that is sent via email.


# Technology Stack

* Django & Django Rest Framework used for making an API <br>
* DjangoQ & Redis were used for asynchronous tasks as well as task scheduling. The scraper runs daily to check for new posts/stories. <br>
* Database is SQLite for development purposes. <br>
* Pytorch for the Image Captioning Model. **Note:** the model is pretty bad, as it is not implemented with attention and was trained for only 7-8 epochs on Google Collab. The smallest dataset (Flickr8) was used for this task. Future improvements are coming. <br>

## Frontend
React & Material UI used to make it responsive.

