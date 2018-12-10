# Pricosha

Pricosha
  A system for privately sharing content items among groups of people.

All Available Features:
  View Public Content
  Login
  View Shared Content and Info About Them
  Manage Tags
  Post Content Item
  Tag Content Item
  Add Friend
  
  Optional Features:
    1. Add Comment
    2. Defriend

Team Members and Contributions:
  1. Payal Naresh
      View Public Content
      Login
      View Shared Content and Info About Them
      Manage Tags
      Add Friend
      Defriend

  2. Tracy Joseph
      Post Content Item
      Tag Content Item
      Add Comment

Optional Features Explained:
    1. Add Comment
        A. Team Member: Tracy Joseph
        B. User can add comments about content item that is visible to them.
        C. Adding this to Pricosha would be a good feature becasue it allows users to comment on posts and interact with each other  
        D. To the database schema, the following table needed to be added:
            CREATE TABLE Comment( commentor_email VARCHAR(20), 
                                  item_id int,             
                                  comment VARCHAR(1000),           
                                  PRIMARY KEY(commentor_email, item_id), 
                                  FOREIGN KEY (commentor_email) REFERENCES Person(email), 
                                  FOREIGN KEY(item_id)REFERENCES ContentItem(item_id) 
                                  );
            This creates a table called Comment, with the attributes email, item_id, and comment. The email is is email of the 
            person who commented and tells us the item they commented on and what they said.
        E. To implement this feature the following query was used:
           comment_query = 'INSERT INTO Comment(commentor_email, item_id, comment) VALUES(%s, %s, %s)
        F. You can find the source code for this feature in Pricosha.py (@app.route('/comment'))
        G. https://pastepic.xyz/image/0MsoC 
        
    2. Defriend
        A. Team Member: Payal Naresh
        B. The user can input the friendgroup they would like to access, and the first and last names of the person they 
           wish to remove from their friendgroup. Only users who own friendgroup can remove somebody from their friendgroup,
           and the friend will no longer be a part of tha friendgroup in the belong table. If the user did not own the friendgroup
           or the friend they wanted ti remove was not a part of the friendgroup, Pricosha informs the user.
        C. Defriend is a good feature to have because it allows a friendgroup owner to remove members of their friendgroup.
        D. No change to the database are necessary.
        E. 
           - To check whether the user owns the friendgroup:
              friendGroupQuery = 'SELECT fg_name FROM friendgroup WHERE owner_email = %s AND fg_name = %s'
           - To check if the friend you want to defriend is part of the friendgroup
              queryFindFriend = 'SELECT belong.email FROM belong Natural Join person WHERE fg_name = %s AND\
                           owner_email = %s AND fname = %s AND lname = %s'
           - To remove person from friendgroup and update the belong table
              queryDelete = 'DELETE FROM belong WHERE email = %s AND owner_email = %s AND fg_name = %s'
        F. You can find the source code for this feature in Pricosha.py (@app.route('/defriend', methods=['GET', 'POST']))
        G. Screenshot: https://pastepic.xyz/image/0Mmba
           
