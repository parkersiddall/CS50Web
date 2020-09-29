document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

});

//FUNCTIONS

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#message-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  // listen for the submission of the form
  document.querySelector('form').onsubmit = () => {

      // POST to server
      fetch('/emails', {
          method: 'POST',
          body: JSON.stringify({
              recipients: document.querySelector('#compose-recipients').value,
              subject: document.querySelector('#compose-subject').value,
              body: document.querySelector('#compose-body').value,
          })
        })
        .then(response => response.json())
        .then(result => {
            // Print result
            console.log(result);

        });

        // momentary wait so that the server has time to store the message before loading the mailbox
        setTimeout(function(){
            // run load_mailbox function for sent
            load_mailbox('sent');
        }, 1000);

        // return false to block the form from going to a different page
        return false;
  }
}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#message-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // gather emails from server
  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
        // Print emails
        console.log(emails);

        // run function to add email
        emails.forEach(add_email);
    });
}

// for each email creates a div for it to be displayed
function add_email(email){

    // Create div row for message
    const message_div = document.createElement('div');

    // add event listener to the div in order to access message page
    message_div.addEventListener('click', function() {
    console.log(`${email.id}`) // load function for message-view
    load_message(email.id);
    });

    // add condition for read status. gray if already read, white if new
    if (email.read === false){
        message_div.className = 'email_line_unread';
    } else if (email.read === true){
        message_div.className = 'email_line_read';
    }


    // create span for subject
    const subject = document.createElement('span');
    subject.innerHTML = email.subject;
    subject.className = 'subject';

    // create span for sender
    const sender = document.createElement('span');
    sender.innerHTML = email.sender;
    sender.className = 'sender';

    // create span for date sent
    const date = document.createElement('span');
    date.innerHTML = email.timestamp;
    date.className = 'date';

    // add the spans to the div
    message_div.append(sender);
    message_div.append(subject);
    message_div.append(date);

    // Add post to DOM
    document.querySelector('#emails-view').append(message_div);
}

function load_message(id){
    // manage displays for other div views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#message-view').style.display = 'block';

    // hide archive button
    document.querySelector('#archive-button').style.display = 'none';

    // query server for message
    fetch(`/emails/${id}`)
    .then(response => response.json())
    .then(email => {
        // Print email
        console.log(email);

        // modify HTML tags and insert message data
        document.querySelector('#message-sender').innerHTML = email.sender;
        document.querySelector('#message-recipients').innerHTML = email.recipients;
        document.querySelector('#message-subject').innerHTML = email.subject;
        document.querySelector('#message-timestamp').innerHTML = email.timestamp;
        document.querySelector('#message-body').innerHTML = email.body;

        // identify user from the HTML code, which gets it from the Django server
        user = document.querySelector('#user').innerHTML;

        // conditional statement for archive button based on archive status and sender/user info
        if (email.archived === false && email.sender != user){
            document.querySelector('#archive-button').style.display = 'inline'; // make button visible
            document.querySelector('#archive-button').innerHTML = 'Archive'; // button text = archive

        } else if (email.archived === true && email.sender != user){
            document.querySelector('#archive-button').style.display = 'inline'; //show button
            document.querySelector('#archive-button').innerHTML = 'Unarchive'; // button text = unarchive
        }
    });

    // update read status to true because email has been opened
    fetch(`/emails/${id}`, {
      method: 'PUT',
      body: JSON.stringify({
          read: true
      })
    })

    // event listener for click archive button
    document.querySelector('#archive-button').onclick = () => {
        //conditional statement to change action of button
        if (document.querySelector('#archive-button').innerHTML == "Archive"){
            fetch(`/emails/${id}`, {
              method: 'PUT',
              body: JSON.stringify({
                  archived: true
              })
            })
            alert('Email archived!')
        } else if (document.querySelector('#archive-button').innerHTML == "Unarchive") {
            fetch(`/emails/${id}`, {
              method: 'PUT',
              body: JSON.stringify({
                  archived: false
              })
            })
            alert('Email unarchived!')
        }
        // load the inbox
        load_mailbox('inbox');
    }

    // event listener for click reply button
    document.querySelector('#reply-button').onclick = () => {
        fetch(`/emails/${id}`)
        .then(response => response.json())
        .then(email => {
            // show compose view, hide others
            document.querySelector('#emails-view').style.display = 'none';
            document.querySelector('#message-view').style.display = 'none';
            document.querySelector('#compose-view').style.display = 'block';

            // Fill in composition fields
            document.querySelector('#compose-recipients').value = email.sender;
            // conditional statement for RE in Subject
            if (email.subject.slice(0,4) != 'Re: ') {
                document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
            } else {
                document.querySelector('#compose-subject').value = email.subject;
            }

            document.querySelector('#compose-body').value = ` On ${email.timestamp} ${email.sender} wrote: \n ${email.body}`;

            // listen for the submission of the form
            document.querySelector('form').onsubmit = () => {

                // POST to server
                fetch('/emails', {
                    method: 'POST',
                    body: JSON.stringify({
                        recipients: document.querySelector('#compose-recipients').value,
                        subject: document.querySelector('#compose-subject').value,
                        body: document.querySelector('#compose-body').value,
                    })
                  })
                  .then(response => response.json())
                  .then(result => {
                      // Print result
                      console.log(result);

                  });

                  // momentary wait so that the server has time to store the message before loading the mailbox
                  setTimeout(function(){
                      // run load_mailbox function for sent
                      load_mailbox('inbox');
                  }, 1000);

                  // return false to block the form from going to a different page
                  return false;
            }
        });
    }
}
