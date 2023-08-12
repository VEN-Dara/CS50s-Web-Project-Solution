document.addEventListener("DOMContentLoaded", function () {
    // Use buttons to toggle between views
    document.querySelector("#inbox").addEventListener("click", () => load_mailbox("inbox"));
    document.querySelector("#sent").addEventListener("click", () => load_mailbox("sent"));
    document.querySelector("#archived").addEventListener("click", () => load_mailbox("archive"));
    document.querySelector("#compose").addEventListener("click", compose_email);

    //Send email
    document.querySelector('#compose-form').addEventListener("submit", send_email);

    // By default, load the inbox
    load_mailbox("inbox");
});

function reply_email(email_id) {
    fetch(`emails/${email_id}`)
    .then(response => response.json())
    .then(email => {

        document.querySelector("#emails-view").style.display = "none";
        document.querySelector("#compose-view").style.display = "block";

        document.querySelector("#compose-recipients").value = `${email.sender}`;
        document.querySelector("#compose-body").value = `On ${email.timestamp} ${email.sender} wrote: \n${email.body}`;
        if(email.subject.includes("Re: ")) {
            document.querySelector("#compose-subject").value = `${email.subject}`;
        }
        else {
            document.querySelector("#compose-subject").value = `Re: ${email.subject}`;
        }
    })
}

function view_email(email_id) {
    fetch(`emails/${email_id}`)
    .then(response => response.json())
    .then(email => {

        let archivedBtn = email.archived ? 'Unarchive' : 'Archive';
        let archivedClass = email.archived ? 'btn btn-light' : 'btn btn-dark';

        const emailView = document.createElement('div')
        emailView.classList.add("email-view");
        emailView.innerHTML = `
            <hr>
            <p><Strong>Form:</Strong> ${email.sender}</p>
            <p><strong>To:</strong> ${email.recipients}</p>
            <p><strong>Subject:</strong> ${email.subject}</p>
            <p><strong>Timestamp:</strong> ${email.timestamp}</p>
            <button class="btn btn-outline-primary" id="reply-btn">Reply</button>
            <button class="btn ${archivedClass}" id="archived-btn">${archivedBtn}</button>
            <hr>
            <p class="view-email-body">${email.body}</p>
        `;

        document.querySelector('#emails-view').innerHTML = emailView.outerHTML;

        //Update read status
        if(!email.read) {
            fetch(`/emails/${email.id}`, {
                method : 'PUT',
                body : JSON.stringify({
                    read : true
                })
            })
        }

        //Archived btn
        const archiveBtn = document.querySelector('#archived-btn');
        archiveBtn.addEventListener('click', function() {
            fetch(`/emails/${email.id}`, {
                method : 'PUT',
                body : JSON.stringify({
                    archived : !email.archived
                })
            })
            .then(() => { load_mailbox('archive') });
        })

        //Reply email
        document.querySelector('#reply-btn').addEventListener('click', function() {
            reply_email(email.id);
        });
        
    });

}

function compose_email() {
    // Show compose view and hide other views
    document.querySelector("#emails-view").style.display = "none";
    document.querySelector("#compose-view").style.display = "block";

    // Clear out composition fields
    document.querySelector("#compose-recipients").value = "";
    document.querySelector("#compose-subject").value = "";
    document.querySelector("#compose-body").value = "";
}

function load_mailbox(mailbox) {
    // Show the mailbox and hide other views
    document.querySelector("#emails-view").style.display = "block";
    document.querySelector("#compose-view").style.display = "none";

    // Show the mailbox name
    document.querySelector("#emails-view").innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

    //Get mail
    fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
        console.log(emails);
        emails.forEach(email => {

            const newEmail = document.createElement('div');
            newEmail.classList.add('list-group-item');
            newEmail.innerHTML = `
            <p><strong>${email.sender}</strong></p>
            <p>${email.subject}</p>
            <p>Subject: ${email.timestamp}</p>
            `;
            
            read = email.read ? 'read' : 'unread';
            newEmail.classList.add(read);
            
            newEmail.addEventListener('click', function() {
                view_email(email.id);
            })

            document.querySelector('#emails-view').append(newEmail);
        })
    });
}

function send_email(event) {
    event.preventDefault();

    const recipient = document.querySelector("#compose-recipients").value;
    const subject = document.querySelector("#compose-subject").value;
    const body = document.querySelector("#compose-body").value;

    fetch('/emails', {
        method: 'POST',
        body: JSON.stringify({
            recipients: recipient,
            subject: subject,
            body: body
        })
    })
    .then(() => load_mailbox('sent'));

}

