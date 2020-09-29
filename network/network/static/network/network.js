document.addEventListener('DOMContentLoaded', function() {

    // load jquery
    var script = document.createElement("SCRIPT");
    script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js';
    script.type = 'text/javascript';
    document.getElementsByTagName("head")[0].appendChild(script);

    // identify all of the buttons that have the .edit class
    document.querySelectorAll('.edit').forEach(function(item) {
        // event listener for click on an item with .edit class
      item.addEventListener('click', function() {
          // log it's ID
        console.log(`${event.srcElement.id} edit in progress.`);
        // slice the id of the edit ID to single out the posts // ID
        var id = event.srcElement.id.slice(5);

        // hide the post content, show the edit form
        document.querySelector(`#content_${id}`).style.display = 'none';
        document.querySelector(`#edit_form_${id}`).style.display = 'block';

        // listener for edit form submission
        document.querySelector(`#edit_form_${id}`).onsubmit = () => {
            console.log(document.querySelector(`#textarea_${id}`).value);

            fetch('/edit', {
                 method: 'POST',
                 body: JSON.stringify({
                     edited_content: document.querySelector(`#textarea_${id}`).value,
                     post_id: id,
                 })
               })
               .then(response => response.json())
               .then(result => {
                   // Print result
                   console.log(result);
               });


            // update innerHTML of post
            document.querySelector(`#content_${id}`).innerHTML = document.querySelector(`#textarea_${id}`).value;

            // hide form, show post
            document.querySelector(`#content_${id}`).style.display = 'block';
            document.querySelector(`#edit_form_${id}`).style.display = 'none';
            return false;
        }

        });
    });

    // selector for unlike button
    document.querySelectorAll('.unlike').forEach(function(item) {
        // add a listener for the click
         item.addEventListener('click', function() {

             console.log(`${event.srcElement.id} unlike clicked.`);
             // slice the id of the edit ID to single out the posts // ID
             var id = event.srcElement.id.slice(7);

             // send info to database
             fetch('/unlike', {
                  method: 'POST',
                  body: JSON.stringify({
                      post_id: id,
                  })
                })
                .then(response => response.json())
                .then(result => {
                    // Print result
                    console.log(result);
                });

            // update content of div on the webpage with 1 second wait
            setTimeout(function(){
                $( `#postlikes_${id}` ).load(location.href + ` #postlikes_${id}` );

                // hide unlike
                // show like
                document.querySelector(`#like_${id}`).style.display = 'inline';
                document.querySelector(`#unlike_${id}`).style.display = 'none';

            }, 0500);

         })
    })

    // selector for like button
    document.querySelectorAll('.like').forEach(function(item) {
        // add a listener for the click
         item.addEventListener('click', function() {

             console.log(`${event.srcElement.id} like clicked.`);
             // slice the id of the edit ID to single out the posts // ID
             var id = event.srcElement.id.slice(5);

             // send info to database
             fetch('/like', {
                  method: 'POST',
                  body: JSON.stringify({
                      post_id: id,
                  })
                })
                .then(response => response.json())
                .then(result => {
                    // Print result
                    console.log(result);
                });

            // update content of div on the webpage with 1 second wait
            setTimeout(function(){
                $( `#postlikes_${id}` ).load(location.href + ` #postlikes_${id}` );

                // hide like
                // show unlike
                document.querySelector(`#like_${id}`).style.display = 'none';
                document.querySelector(`#unlike_${id}`).style.display = 'inline';

                document.querySelector()
            }, 0500);


         })
    })


})
