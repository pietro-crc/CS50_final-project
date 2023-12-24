from hmac import new
from platform import mac_ver
import re
from flask import app,jsonify
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
import pandas as pd
import langid
from sympy import li
from tool import StratifiedSampling, YTlinkconverter as converter
from tool import  StratifiedSampling 
from selenium.webdriver.common.action_chains import ActionChains
import concurrent.futures
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import logging
from stanza import DownloadMethod
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import stanza
import concurrent.futures
from cs50 import SQL
from flask import Flask
import os
from flask import abort
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask import redirect, url_for
from helpers import apology, login_required
import threading
import datetime
import locale

# language setting for the date time scraped in the video 
locale.setlocale(locale.LC_TIME, "it_IT")


logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
logger.setLevel(logging.WARN)

app = Flask(__name__)


#cookie disabled
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
ss= StratifiedSampling()
global a
a =[]

db = SQL("sqlite:////Users/pietrocaracristi/Desktop/WEB_DEVELOPMENT/PROGETTO/database.db")

#questo va inserito in un database perchè se no fa conflitto !!!!!
processo_completato = False 

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route("/")
def index():
    """Show homepage"""
    return render_template('login.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method =="POST":
        name = request.form.get('username')
        password = request.form.get('password')
        check = request.form.get('confirmation')
        if (name == "" or password == ""):
            return abort(400)
        if password != check:
            print('NOT CORRECT')
            flash("Password don't match. Try again.")
            return render_template('register.html')


        else:
            if len(db.execute("SELECT * FROM users WHERE username = ?",name))>0:
                flash("USER ALREADY REGISTERED!")
                
                return render_template('register.html')

            else:
                try:
                    if password is not None:
                    
                        hash= generate_password_hash(password, method = 'scrypt', salt_length =16)
                        db.execute("INSERT  INTO users (username,hash) VALUES(?,?)",name,hash)
                        flash('user registered')
                except:
                    print('BIG ERRORRRRRRRRRRRR!!!!')

    return render_template('register.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        password1 = request.form.get("password")
        
       
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"],password1):  # type: ignore
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page, CHANGEEEEEEEEE
        return redirect("/link")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    

@app.route("/link" , methods=["GET", "POST"])
@login_required
def link():
    session['user_id'] = 2
    """Link page"""
    if request.method == "POST":
        link = request.form.get('link')
        if ss.is_youtube_channel_url(link):
            db.execute('INSERT INTO channel (url,user_id) VALUES (?,?)',link,session['user_id'])
            return render_template('loading.html')
        else:
            flash('link not valid')
            return render_template('link.html')
    return render_template('link.html')



status_function= 0



@app.route('/start_processes', methods =["GET", "POST"])
@login_required
def start_processes():
    

    def elaborate(link,session_thread):
        

        file_path_chrome = '/Users/pietrocaracristi/PycharmProjects/pythonProject-1-12/day_53_capstone_zillo/chromedriver'
        service = Service(executable_path=file_path_chrome)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_experimental_option("detach", True)

        # service sono validi solo per questo computer , per visual studio bisogna togliere service  e lasciare solo .chrome()
        driver = webdriver.Chrome(options=options, service=service)


        link= link
        # strumento per convertire il link
        cv = converter(link)

        driver.get(link)

        time.sleep(4)

        element = driver.find_element(by='xpath',value='//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[4]/div[1]/form[2]/div/div/button')
        element.click()

        time.sleep(3)

        # find all element by selector comment you tube
        all_videos_button = driver.find_element(by='xpath',value='//*[@id="tabsContent"]/yt-tab-group-shape/div[1]/yt-tab-shape[2]' )
        all_videos_button.click()
        time.sleep(1)
        most_recent = driver.find_element(by='xpath',value="//yt-tab-shape[@tab-title='Video']")
        most_recent.click()

        #add 10% to the loading if the scraping of the video was successful
        print('adesso aggiorna il database di statuzzzzzzzzzzzzzzzzzzzzzzzzzz')
        
        try:
            db.execute('INSERT INTO status (status,user_id, percent) VALUES (?,?,?)',"status",session_thread,10)
        
        except:
            db.execute('UPDATE status SET percent = ? WHERE user_id = ?',10,session_thread)
        error = 0
       


        # Esegui il clic sull'elemento, questo va sopraaaaaaaa

        time.sleep(2)
        for i in range(1, 1):  # carica i commenti
            driver.execute_script("window.scrollBy(0, 600);")
            time.sleep(0.2)


        all_video = driver.find_elements(by='id', value="video-title-link")
        print('all video lenght !!!!!!!!',len(all_video))

        print('helloooo',len(all_video))
        
        sampling_video = ss.sampler(total=all_video, group=10)
        new_list = sampling_video
        print('len list video ooooooo',len(new_list))
        print('new list videooooooooo',new_list)


        all_video= new_list 
        

        #video_url = all_video[0].get_attribute('href')  # ottieni l'URL del video
        #print(video_url)
        #driver.execute_script(f'window.open("{video_url}","_blank");')
        #all_video[2].send_keys(Keys.CONTROL + Keys.RETURN)
        # find all element by xpath comment you tube
        #comments = driver.find_elements(by='xpath',value='//*[@id="content-text"]')  # recupera tutti gli elementi con l'id content-text

 

        def scrape_comments(video, video_id,db):
            
            global status_function
            global error
            '''
            scrape all the comments on the related video, only for one video, use a for loop or while loop to estract
            all the comment in a channel
            insert the video in the database with the list of video
            insert all the comment in the database comments
            Args:
            video (str): a webelement of selenium
            video_id (int) : the n° of the video

            Returns:
            str: the extracted comment from the video
            '''
            driver = webdriver.Chrome(options=options, service=service)
            try:


                # click the webelement and load the video page
                video_url = video.get_attribute('href')  # ottieni l'URL del video
                print(video_url)
                driver.get(video_url)
                # Attendere fino a quando l'elemento cookie è presente
                time.sleep(4)
                try:
                    element2 = (WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div[2]/div[6]/div[1]/ytd-button-renderer[1]/yt-button-shape/button'))))
                    element2.click()
                    #wait = WebDriverWait(driver, 30)
                    #cookie = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div[2]/div[6]/div[1]/ytd-button-renderer[1]/yt-button-shape/button')))
                    time.sleep(1)
                    #cookie.click RIPETIZIONE DEL CODICE PERCHè DAVA PROBLEMI QUEST TRY==
                    print('oneeee')
                    time.sleep(3)

                #except:
                    #button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'yt-spec-button-shape-next yt-spec-button-shape-next--filled yt-spec-button-shape-next--mono yt-spec-button-shape-next--size-m')))
                    #button.click()
                    #print('twoooooo')
                except:

                    element1 = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Accetta l\'utilizzo dei cookie e di altri dati per le finalità descritte"]')))
                    element1.click()
                    print('threreeeee')



                time.sleep(3)
                wait = WebDriverWait(driver, 20)
                date = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="expand"]')))
                date.click()
                #prendere il 3 elemento di date 
                time.sleep(2)
                date = driver.find_element(by='xpath', value='/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[4]/div[1]/div/ytd-watch-info-text/div/yt-formatted-string/span[3]')
                print(date.text)
                date = date.text

                #NB importance of the language of the date !! ! ! !  ! ! ! ! ! !  ! ! ! ! ! ! !  ! ! ! ! ! ! ! ! ! !  ! ! ! ! !  ! ! ! ! !  ! ! ! ! !  !!
                try:

                    #convert data to datetime 
                    data_datetime = datetime.datetime.strptime(date, "%d %b %Y")
                except:
                    data_stringa = date.split("il giorno ")[1]

                    data_datetime = datetime.datetime.strptime(data_stringa, "%d %b %Y")





                for i in range(1, 50):  # carica i commenti
                    driver.execute_script("window.scrollBy(0, 900);")
                    time.sleep(0.2)

                time.sleep(2)
                # create a list of comments of the video
                comments = driver.find_elements(by='xpath', value='//*[@id="content-text"]')
                strip_comments = ss.sampler(total=comments, group=100)
               
                if not strip_comments:

                    driver.close()
                    return

                # current time in a format compatible for sqlite datetime
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                url = driver.current_url
                time.sleep(1)
                try:
                    # insert the video in the video table
                    db.execute("INSERT INTO video (user_id,video_id,data,url) VALUES (?,?,?,?)", session_thread,video_id, data_datetime, url)
                    for elemen in strip_comments:
                        print(elemen.text)
                        db.execute("INSERT INTO comments (user_id, comment,data,url) VALUES (?,?,?,?)", session_thread, elemen.text,current_time, url)

                        comment_id = db.execute("SELECT id FROM comments WHERE comment = ?", elemen.text)[0]
                        print(comment_id)
                        print(comment_id['id'])
                        video_id = db.execute("SELECT id FROM video WHERE url = ?", url)[0]
                        print(video_id)
                        print(video_id['id'])

                        db.execute("INSERT INTO video_comment (video_id,comment_id) VALUES (?,?)",video_id['id'], comment_id['id'])

                    current_percent = db.execute("SELECT percent FROM status WHERE user_id = ?", session_thread)[0]
                    updated_percent = current_percent['percent'] + 4
                        
                    db.execute("UPDATE status SET status =?,percent = ? WHERE user_id = ?",'status', updated_percent, session_thread)
                       



                    driver.close()


                except Exception as e :
                    print(f"Si è verificato un errore: {e}")
                    logger.error("Errore SQL", exc_info=True)
                    driver.close()
                    scrape_comments(video, video_id,db)
                   

            except Exception as e:
                driver.close()
                print('big problem')
                print(f"Si è verificato un errore: {e}")
                logger.error("Errore SQL", exc_info=True)
                scrape_comments(video, video_id,db)



        def scrape(all_video):
            def scraper(video):
                global db
                return scrape_comments(video=video, video_id=all_video.index(video),db =db)

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                executor.map(scraper, all_video)
                print('xuxux')





        scrape(all_video)



        time_start= datetime.datetime.now()
        tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-emotion",legacy=False)
        model = AutoModelForSeq2SeqLM.from_pretrained("mrm8488/t5-base-finetuned-emotion")
        nlp = stanza.Pipeline('en', processors='tokenize,sentiment',download_method=DownloadMethod.REUSE_RESOURCES)


        def get_emotion(testo):
            time.sleep(0.1)
            '''
            make for all comment at once the emotion and sentiment analisys and add in the relative column

            Args:
            testo (str): a dictionary with the text as {'comment':text}

            Returns:
            str: true if successful
            '''
            try:
                print(testo)
                frase = testo['comment']
                id = testo['id']

                input_ids = tokenizer.encode(frase + '</s>', return_tensors='pt')

                output = model.generate(input_ids=input_ids,
                                        max_length=2)

                dec = [tokenizer.decode(ids) for ids in output]
                label = dec[0]

                '''analisi del sentiment sulla frase'''
                doc = nlp(frase)  # analisi del sentiment sulla frase

                sentiment = doc.sentences[0].sentiment  # type: ignore # risultato del sentiment
                # Stampa il risultato


                sentimento = int(sentiment)

                print(sentimento, label)
                label = label.split(' ')
                label = str(label[1])
                #id_comment= db.execute("SELECT id FROM comments WHERE comment = ?", frase)[0]
                #id_comment = id_comment['id']
                #print('this is the id of the comment commentssss',id_comment)
                #insert sentiment and emotion in database
                try:
                    db.execute("UPDATE comments SET sentiment = ?, emotion = ? WHERE id = ?", sentimento, label, id)
                except Exception as e:
                    print(f"Si è verificato un errore in sentiment comment: {e}")
                    logger.error("Errore SQL comment sentimen", exc_info=True)
                    return False
                
                #add one to the status db
                current_percent = db.execute("SELECT percent FROM status WHERE user_id = ?", session_thread)[0]
                updated_percent = current_percent['percent'] + 1
                            
                db.execute("UPDATE status SET percent= ? WHERE user_id = ?", updated_percent, session_thread)
            except Exception as e:
                print(f"Si è verificato un errore: {e}")
                logger.error("Errore SQL ultimooooooo", exc_info=True)
            return True

        comments = db.execute("SELECT comment,id FROM comments WHERE user_id = ? AND (sentiment IS NULL OR sentiment = '') AND (emotion IS NULL OR emotion = '')",session_thread)
        
    
        
        time_start= datetime.datetime.now()
        #sent = db.execute("SELECT comment FROM comments WHERE user_id = ?",session_thread)[0]
        #sent =sent['comment']
        #print(sent)

        #for comment in comments:
            #get_emotion(comment)
        time_end= datetime.datetime.now()
        print(time_end-time_start)

        #analisys all at once
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(get_emotion,comments)
        
        time_end= datetime.datetime.now()
        print(time_end-time_start)


        print('finish threading elementssssssssssss comments')

        #update status to true
        db.execute("UPDATE channel SET status = ? WHERE user_id = ?", 'True',session_thread)
        
        count_video =0
        for video in all_video:
            #insert the result in video to facilitate the use in the result page
            try:

                time.sleep(0.1)
                video_url = video.get_attribute('href')
                print(video_url)
                video_id = db.execute("SELECT id FROM video WHERE url = ?", video_url)[0]
                print(video_id)
                print('this is the videooooooooo idddddddddddddd NECESSARYYYYYYYYYYYYYYYYYYYYYYYYYY',video_id['id'])
                
                def result(url):
                    negative = db.execute("SELECT COUNT(*) FROM comments WHERE id  IN(SELECT comment_id FROM video_comment WHERE video_id=?) AND sentiment = ?",video_id['id'],0)
                    print('negativeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',negative)
                    negative = negative[0]['COUNT(*)']


                    positive = db.execute("SELECT COUNT(*) FROM comments WHERE id  IN(SELECT comment_id FROM video_comment WHERE video_id=?) AND sentiment = ?",video_id['id'],2)
                    positive = positive[0]['COUNT(*)']
                    neutral = db.execute("SELECT COUNT(*) FROM comments WHERE id  IN(SELECT comment_id FROM video_comment WHERE video_id=?) AND sentiment = ?",video_id['id'],1)
                    neutral = neutral[0]['COUNT(*)']

                    total = db.execute("SELECT COUNT(*) FROM comments WHERE id IN(SELECT comment_id FROM video_comment WHERE video_id=?)",video_id['id'])
                    total = total[0]['COUNT(*)']
                    
                    print('negative',negative)
                    print('positive',positive)
                    print('neutral',neutral)
                    print('total',total)
                    #emotion 
                    anger = db.execute("SELECT COUNT(*) FROM comments WHERE id  IN(SELECT comment_id FROM video_comment WHERE video_id=?) AND emotion = ?",video_id['id'],'anger')
                    print('anger',anger)
                    anger = anger[0]['COUNT(*)']
                    fear = db.execute("SELECT COUNT(*) FROM comments WHERE id  IN(SELECT comment_id FROM video_comment WHERE video_id=?) AND emotion = ?",video_id['id'],'fear')
                    print('fear',fear)
                    fear = fear[0]['COUNT(*)']
                    joy = db.execute("SELECT COUNT(*) FROM comments WHERE id  IN(SELECT comment_id FROM video_comment WHERE video_id=?) AND emotion = ?",video_id['id'],'joy')
                    joy = joy[0]['COUNT(*)']
                    love = db.execute("SELECT COUNT(*) FROM comments WHERE id  IN(SELECT comment_id FROM video_comment WHERE video_id=?) AND emotion = ?",video_id['id'],'love')
                    love = love[0]['COUNT(*)']
                    sadness = db.execute("SELECT COUNT(*) FROM comments WHERE id  IN(SELECT comment_id FROM video_comment WHERE video_id=?) AND emotion = ?",video_id['id'],'sadness')
                    sadness = sadness[0]['COUNT(*)']
                    surprise = db.execute("SELECT COUNT(*) FROM comments WHERE id  IN(SELECT comment_id FROM video_comment WHERE video_id=?) AND emotion = ?",video_id['id'],'surprise')
                    surprise = surprise[0]['COUNT(*)']
                    total_emotion = db.execute("SELECT COUNT(*) FROM comments WHERE id IN(SELECT comment_id FROM video_comment WHERE video_id=?)",video_id['id'])
                    total_emotion = total_emotion[0]['COUNT(*)']
                    print('anger',anger)
                    print('fear',fear)
                    print('joy',joy)
                    print('love',love)
                    print('sadness',sadness)
                    print('surprise',surprise)
                    print('total emotion',total_emotion)
                    #update the database
                    db.execute("UPDATE video SET negative = ?, positive = ?, neutral = ?, total_sentiment = ?, anger = ?, fear = ?, joy = ?, love = ?, sadness = ?, surprise = ?, total_emotion = ? WHERE id = ?",negative,positive,neutral,total,anger,fear,joy,love,sadness,surprise,total_emotion,video_id['id'])
                    print('finish update video')

                    time.sleep(1)
                    
                    return 'finish'
                    count_video +=1
            except:
                print('error in result')
                
                continue
            result(video_url)




        driver.quit()
        return 'finish'
    #last video input in the database    
    link = db.execute("SELECT url FROM channel WHERE user_id = ?", session['user_id'])
    link = link[-1]['url']
    num = session.get('user_id')
    
    print('hellooooo',num)
    process_thread = threading.Thread(target=elaborate, args=(link,num,))
    process_thread.start()
    
    return 'starting'


@app.route('/status')
def generate():
    
    try:
        result = db.execute("SELECT * FROM status WHERE user_id = ?", session['user_id'])

        status = result[-1]['percent']

        if status > 50 :
            status = db.execute('SELECT percent FROM status WHERE user_id =?',session['user_id'])
            print(status)
            if status[-1]['percent'] is not None:
                status = status[-1]['percent']
                divisor = float(status)/50 

                if status > 70:
                    status = ((float(status)-50)/ divisor)
                    
                    status = round(status)+50
                    if status >60:
                        status_t_F = db.execute('SELECT status FROM channel WHERE user_id =?',session['user_id'])
                        status_t_F = status_t_F[-1]['status']
                        if status_t_F:
                            return jsonify({'value': int(100)})
                    
                    return jsonify({'value': int(status)})
                
                return jsonify({'value': int(status)})
            else:
                status = 0
        else:
            return jsonify({'value': int(status)})
    except:
        status = 0
    
        
    return jsonify({'value': int(status)})


@app.route('/process_status')
@login_required
def process_status():
    process_completed= db.execute('SELECT status FROM channel WHERE user_id =?',session['user_id'])
    process_completed = process_completed[-1]['status']

    if process_completed:
        
        #reset status percent
        db.execute("UPDATE status SET percent = ? WHERE user_id = ?", 0, session['user_id'])
        return 'complete'
    else:
        return 'incomplete'
    

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/link')

@app.route('/result')
@login_required
def result():

    negative = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND sentiment = ?",session['user_id'],0)
    negative = negative[0]['COUNT(*)']
    positive = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND sentiment = ?",session['user_id'],2)
    positive = positive[0]['COUNT(*)']
    neutral = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND sentiment = ?",session['user_id'],1)
    neutral = neutral[0]['COUNT(*)']
    total = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ?",session['user_id'])
    total = total[0]['COUNT(*)']
    print('negative',negative)
    print('positive',positive)
    print('neutral',neutral)
    print('total',total)
    #emotion 
    anger = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND emotion = ?",session['user_id'],'anger')
    anger = anger[0]['COUNT(*)']
    fear = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND emotion = ?",session['user_id'],'fear')
    fear = fear[0]['COUNT(*)']
    joy = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND emotion = ?",session['user_id'],'joy')
    joy = joy[0]['COUNT(*)']
    love = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND emotion = ?",session['user_id'],'love')
    love = love[0]['COUNT(*)']
    sadness = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND emotion = ?",session['user_id'],'sadness')
    sadness = sadness[0]['COUNT(*)']
    surprise = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND emotion = ?",session['user_id'],'surprise')
    surprise = surprise[0]['COUNT(*)']
    total_emotion = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ?",session['user_id'])
    total_emotion = total_emotion[0]['COUNT(*)']
    print('anger',anger)
    print('fear',fear)
    print('joy',joy)
    print('love',love)
    print('sadness',sadness)
    print('surprise',surprise) 

    #data connected to the date of the video
    last_channel = db.execute("SELECT * FROM channel WHERE user_id = ? ",session['user_id'])[-1]
    last_channel = last_channel['id']
    print(last_channel)

    list_of_video = db.execute("SELECT * FROM video WHERE video_id = ?",last_channel)
    
    data_video_sentiment_total = []
    sum_data_sentiment =[]
    data_video_sentiment_positive = []
    data_video_sentiment_negative = []
    data_video_sentiment_neutral = []
    datetime_video = []
    for video in list_of_video:
        data_video_sentiment_total.append(video['total_sentiment'])
        data_video_sentiment_positive.append(video['positive'])
        data_video_sentiment_negative.append(video['negative'])
        data_video_sentiment_neutral.append(video['neutral'])
        sum_data_sentiment.append(video['positive']-video['negative'])
        datetime_video.append(video['data'])



    #obtain the data with date and number of comments
    dictionary ={
        'negative':negative,
        'positive':positive,
        'neutral':neutral,
        'total':total,
        'anger':anger,
        'fear':fear,
        'joy':joy,
        'love':love,
        'sadness':sadness,
        'surprise':surprise,
        'total_emotion':total_emotion,
        'data_video_sentiment_total':data_video_sentiment_total,
        'data_video_sentiment_positive':data_video_sentiment_positive,
        'data_video_sentiment_negative':data_video_sentiment_negative,
        'data_video_sentiment_neutral':data_video_sentiment_neutral,
        'sum_data_sentiment':sum_data_sentiment,
        'datetime_video':datetime_video

    }
    print('this is the dictionary', dictionary)
    return render_template('result.html' , data_set = jsonify(dictionary))


@app.route('/result_data')
@login_required
def result_data():

    negative = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND sentiment = ?",session['user_id'],0)
    negative = negative[0]['COUNT(*)']
    positive = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND sentiment = ?",session['user_id'],2)
    positive = positive[0]['COUNT(*)']
    neutral = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND sentiment = ?",session['user_id'],1)
    neutral = neutral[0]['COUNT(*)']
    total = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ?",session['user_id'])
    total = total[0]['COUNT(*)']
    print('negative',negative)
    print('positive',positive)
    print('neutral',neutral)
    print('total',total)
    #emotion 
    anger = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND emotion = ?",session['user_id'],'anger')
    anger = anger[0]['COUNT(*)']
    fear = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND emotion = ?",session['user_id'],'fear')
    fear = fear[0]['COUNT(*)']
    joy = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND emotion = ?",session['user_id'],'joy')
    joy = joy[0]['COUNT(*)']
    love = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND emotion = ?",session['user_id'],'love')
    love = love[0]['COUNT(*)']
    sadness = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND emotion = ?",session['user_id'],'sadness')
    sadness = sadness[0]['COUNT(*)']
    surprise = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ? AND emotion = ?",session['user_id'],'surprise')
    surprise = surprise[0]['COUNT(*)']
    total_emotion = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ?",session['user_id'])
    total_emotion = total_emotion[0]['COUNT(*)']
    print('anger',anger)
    print('fear',fear)
    print('joy',joy)
    print('love',love)
    print('sadness',sadness)
    print('surprise',surprise) 

    #data connected to the date of the video
    last_channel = db.execute("SELECT * FROM channel WHERE user_id = ? ",session['user_id'])[-1]
    last_channel = last_channel['id']
    print(last_channel)

    list_of_video = db.execute("SELECT * FROM video WHERE video_id = ? ORDER by data",last_channel)
    
    
    data_video_sentiment_total = []
    sum_data_sentiment =[]
    data_video_sentiment_positive = []
    data_video_sentiment_negative = []
    data_video_sentiment_neutral = []
    datetime_video = []
    for video in list_of_video:
        data_video_sentiment_total.append(video['total_sentiment'])
        data_video_sentiment_positive.append(video['positive'])
        data_video_sentiment_negative.append(video['negative'])
        data_video_sentiment_neutral.append(video['neutral'])
        sum_data_sentiment.append(video['positive']-video['negative'])
        datetime_video.append(video['data'])



    #obtain the data with date and number of comments
    dictionary ={
        'negative':negative,
        'positive':positive,
        'neutral':neutral,
        'total':total,
        'anger':anger,
        'fear':fear,
        'joy':joy,
        'love':love,
        'sadness':sadness,
        'surprise':surprise,
        'total_emotion':total_emotion,
        'data_video_sentiment_total':data_video_sentiment_total,
        'data_video_sentiment_positive':data_video_sentiment_positive,
        'data_video_sentiment_negative':data_video_sentiment_negative,
        'data_video_sentiment_neutral':data_video_sentiment_neutral,
        'sum_data_sentiment':sum_data_sentiment,
        'datetime_video':datetime_video

    }
    print('this is the dictionary', dictionary)
    return jsonify(dictionary)





if __name__ == '__main__':
    app.run(debug=True)