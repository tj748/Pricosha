#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 3306,
                       user='root',
                       password="",
                       db='pricosha',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
    return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Define route for logout
@app.route('/logout')
def logout():
    return render_template('index.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    email = request.form['email']
    password = request.form['password']
    #password = (request.form['password']).encode()
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM person WHERE email = %s and password = %s'
    cursor.execute(query, (email, password))
    #cursor.execute(query, (email, password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['email'] = email
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Login Failed: Invalid login or email'
        return render_template('login.html', error=error)
    
@app.route('/viewPublicContent')
def viewPublicContent():
    #return 'This is the viewpublicconentpage'
    cursor = conn.cursor()
    query = 'SELECT item_id, email_post, post_time, file_path, item_name FROM contentitem WHERE is_pub = 1 and post_time <= now() + INTERVAL 1 DAY'
    cursor.execute(query)
    #stores the results in a variable
    data = cursor.fetchall()
    cursor.close()
    
    return render_template('viewPublicContent.html', posts = data)
    #use fetchall() if you are expecting more than 1 data row
    
@app.route('/home')
def home():
    user = session['email']
    cursor = conn.cursor();
    query = 'SELECT item_id, email_post, post_time, file_path, item_name\
             FROM contentitem\
             WHERE is_pub = 1 or email_post = %s\
             or item_id in\
                 (SELECT item_id\
                  FROM share\
                  WHERE (owner_email, fg_name ) in\
                  (SELECT owner_email, fg_name\
                   FROM belong\
                   WHERE email = %s AND email in\
                   (SELECT email\
                    FROM belong\
                    WHERE email = %s))) order by post_time desc'
                             
    cursor.execute(query, (user, user, user))
    data = cursor.fetchall()
    
    tagQuery = 'SELECT item_id, email_tagged, fname, lname\
                FROM contentitem Natural Join tag Natural Join person\
                WHERE email_tagged = email AND status = 1'
    cursor.execute(tagQuery)
    tagData = cursor.fetchall()
    
    rateQuery = 'SELECT contentitem.item_id, emoji\
                FROM contentitem Natural Join rate'
                
    cursor.execute(rateQuery)
    rateData = cursor.fetchall()
    
    cursor.close()
    
    return render_template('home.html', email=user, posts=data, tags = tagData, rates = rateData)

@app.route('/manageTag')
def manageTag():
    user = session['email']
    cursor = conn.cursor()
    visibleTagQuery = 'SELECT email_tagger, email_tagged, item_id, item_name, fname, lname, tagtime\
                FROM contentitem Natural Join tag Natural Join person\
                WHERE email_tagger = email AND status = 0'
    cursor.execute(visibleTagQuery)
    visibleTagData = cursor.fetchall() 
    cursor.close()
    
    return render_template('manageTag.html', username = user, manageTags = visibleTagData)

@app.route('/acceptTag', methods=['GET', 'POST'])
def acceptTag():
    user = session['email']
    contentid = request.form['contentid']
    cursor = conn.cursor()
    updatetagquery = 'update tag set status = 1 where email_tagged = %s and item_id = %s' 
    cursor.execute(updatetagquery, (user, contentid))
    cursor.close()
    
    return redirect(url_for('manageTag'))

@app.route('/declineTag', methods=['GET', 'POST'])
def declineTag():
    user = session['email']
    contentid = request.form['contentid']
    cursor = conn.cursor() 
    deleteTagQuery = 'DELETE FROM tag WHERE email_tagged = %s AND item_id = %s'
    cursor.execute(deleteTagQuery, (user, contentid))
    cursor.close()
    
    return redirect(url_for('manageTag'))

@app.route('/postContentItem')
def postContentItem():
    user = session['email']
    cursor = conn.cursor()
    item_name = request.form['item_name']
    file_path = request.form['file_path']
    is_pub = request.form['is_pub']
    if (is_pub == 'public'):
        is_pub = 1
    else:
        is_pub = 0
    query = 'INSERT INTO contentitem (email_post, file_path, item_name, public) VALUES (%s, %s, %s, %s)'
    cursor.execute(query(email, file_path, item_name, is_pub))
    cursor.close()
    return render_template('postcontentitem.html', email = email, data = data)

@app.route('/tagContentItem')
def tagContentItem():
    tagger = session['email']
    cursor = conn.cursor()
    item_id = request.form['item_id']
    taggee = request.form['taggee']
    tagtime = request.form['tagtime']
    error = None
    
    #checks if content is visible to taggee
    public_data_query = 'SELECT * FROM contentitem WHERE is_pub = 1 AND item_id = %s)'
    is_public_data = cursor.execute(public_data_query(item_id))

    #if the item is not public content
    if (not is_public_data):
        error = "This is not public content, so you can not tag"
        
    else:
        # if the user is self-tagging
        if (taggee == tagger):
            self_tag_query = 'INSERT INTO Tag (item_id, email_tagger, email_tagged, tagtime, status) VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(self_tag_query(item_id, tagger, tagger, tagtime, true))

        # if the content item is visible to the taggee
        else:
            tag_query = 'INSERT INTO Tag (item_id, email_tagger, email_tagged, tagtime, status) VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(tag_query(item_id, tagger, taggee, tagtime, false))

    cursor.close()
    return render_template('tagContentItem.html')

@app.route('/addFriend', methods=['GET', 'POST'])
def addFriend():         
    
    user = session['email']
    
    cursor = conn.cursor()
    
    friendGroup = request.form.get('group')

    friendFirst = request.form.get('first_name')
    friendLast = request.form.get('last_name')
    cursor = conn.cursor();
    groupQuery = 'SELECT fg_name FROM friendgroup WHERE fg_name = %s AND owner_email = %s'
    cursor.execute(groupQuery, (friendGroup, user))    
    groupData = cursor.fetchone()
    error = None
    if(groupData):
        queryFriendEmail = 'SELECT belong.email FROM belong WHERE belong.email in\
                 (SELECT person.email FROM person WHERE fname = %s AND lname = %s)\
                 AND fg_name = %s AND owner_email = %s'
        cursor.execute(queryFriendEmail, (friendFirst, friendLast, friendGroup, user))
        friendEmail = cursor.fetchone()
        if(friendEmail):
            error = 'This person is already in the friendgroup!'
            return render_template('addFriend.html', error = error)
        else:
            queryEmail = 'SELECT email FROM person WHERE fname = %s AND lname = %s'
            cursor.execute(queryEmail, (friendFirst, friendLast))
            email = cursor.fetchall();
            if(len(email) > 1):
                error = 'There are multiple people with that name!'
                return render_template('addFriend.html', error = error)
            elif(len(email) == 0):
                error = 'This person does not exist!'
                return render_template('addFriend.html', error = error)
            else:
                insertQuery = 'INSERT INTO belong VALUES (%s, %s, %s)'
                cursor.execute(insertQuery, (email[0]['email'], user, friendGroup))
                conn.commit()
                cursor.close()
                return redirect(url_for('/addFriend'))
    else:
        error = 'This friendgroup does not exist!'
        return render_template('addFriend.html', error = error)


#Extra Features 
@app.route('/comment')
def comment():
    
##    query = 'CREATE TABLE Comment( \
##            commentor_email VARCHAR(20), \
##            item_id int, \
##            comment VARCHAR(1000), \
##            PRIMARY KEY(commentor_email, item_id), \
##            FOREIGN KEY (commentor_email) REFERENCES Person(email), \
##            FOREIGN KEY(item_id)REFERENCES ContentItem(item_id) \
##            );
    

    commentor = session['email']
    cursor = conn.cursor()
    comment_item_id = session['item_id']
    comment = request.form['comment']
    comment_query = 'INSERT INTO Comment(commentor_email, item_id, comment) VALUES(%s, %s, %s)'
    cursor.execute(comment_query(commentor, comment_item_id, comment))
    cursor.close()
    return render_template('comment.html')

@app.route('/defriend', methods=['GET', 'POST'])
def defriend():
    user = session['email']
    selectGroup = request.form.get('select_group')
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    cursor = conn.cursor();
    friendGroupQuery = 'SELECT fg_name FROM friendgroup WHERE owner_email = %s AND fg_name = %s'
    cursor.execute(friendGroupQuery, (user, selectGroup))
    dataGroup = cursor.fetchone();
    error = None
    #Checks if user owns the friendgroup
    if(dataGroup):
        queryFindFriend = 'SELECT belong.email FROM belong Natural Join person WHERE fg_name = %s AND\
                           owner_email = %s AND fname = %s AND lname = %s'
        cursor.execute(queryFindFriend, (selectGroup, user, firstname, lastname))
        findFriend = cursor.fetchone()
        #Checks if the friend you want to defriend is part of the friendgroup
        if(findFriend):
            
            queryDelete = 'DELETE FROM belong WHERE email = %s AND owner_email = %s AND fg_name = %s'
            cursor.execute(queryDelete, (findFriend, user, selectGroup)) 
            cursor.close()
            
            #queryRemoveTag = 'DELETE FROM tag WHERE email_tagger = %s
            return redirect(url_for('defriend'))                   
            
        else:
            error = 'This person is not part of that friendgroup!'
            return render_template('defriend.html', error=error)
        
    else:
        error = 'You do not own this friendgroup!'
        return render_template('defriend.html', error=error) 


app.secret_key = 'some key that you will never guess'

if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
