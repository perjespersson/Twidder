displayView = function(){
    // the code required to display a view
};

window.onload = function(){
    //Code that is executed as the page is loaded.
    //You shall put your own custom code here.
    //Window.alert() is not allowed to be used in your implementation.
    var welcomeView = document.getElementById("welcomeview");
    var profileview = document.getElementById("profileview");
    /*document.body.appendChild(form);*/

    if (localStorage.token != null)
    {
        set_view("profileview");
        establishWebSocket();
        load_stored_stats();
        load_information();
        load_charts()
    }
    else
    {
        set_view("welcomeview");
    }
};

function wsOnOpen(ws)
{
    ws.send(JSON.stringify({"token": localStorage.getItem("token")}))
}

function wsOnMessage(ws, evt)
{
    data = JSON.parse(evt.data)
    if (data['type'] == "stats")
    {
        if ("numPeopleOnline" in data)
        {
            update_people_online(data["numPeopleOnline"]["total"])
            changeOnlineUsers(data["numPeopleOnline"]["total"],
                                data["numPeopleOnline"]["male"],
                                data["numPeopleOnline"]["female"],
                                data["numPeopleOnline"]["other"])
        }
        else if ("TotalNumUsers" in data)
        {
            update_num_accounts(data["TotalNumUsers"]["total"])
            changeTotalUsers(data["TotalNumUsers"]["total"],
                                data["TotalNumUsers"]["male"],
                                data["TotalNumUsers"]["female"],
                                data["TotalNumUsers"]["other"])
        }
        else if ("TotalNumPosts" in data)
        {
            update_num_posts(data["TotalNumPosts"]["total"])
            changeTotalPosts(data["TotalNumPosts"]["total"],
                                data["TotalNumPosts"]["male"],
                                data["TotalNumPosts"]["female"],
                                data["TotalNumPosts"]["other"])
        }
    }
}

function wsOnClose(evt)
{
    set_view("welcomeview");
    localStorage.removeItem("token");
}

function establishWebSocket()
{
    if ("WebSocket" in window) {
        // Let us open a web socket
         ws = new WebSocket("ws://" + document.domain + ":5000/socket");
         ws.onopen = function ()
         {
             wsOnOpen(ws);
         }
         ws.onmessage = function (evt)
         {
             wsOnMessage(ws, evt)
         }
         ws.onclose = function (evt)
         {
             wsOnClose(evt)
         }
    }
    else
    {
        alert("Websockets are not supported in this browser!")
    }
}

function set_view(view_name)
{
    document.getElementById("main_div").innerHTML = document.getElementById(view_name).innerHTML;
    if (view_name == "profileview")
    {
        // Get the element with id="defaultOpen" and click on it
        document.getElementById("defaultOpen").click();
    }
}



function signin_form_request(formData)
{
    var email = formData.login_email.value;
    var password = formData.login_password.value;

    var f = {"email": email, "password": password};
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            req = JSON.parse(this.responseText);
            document.getElementById("login_error").innerHTML = req['message'];
            if (req['pass'])
            {
                localStorage.setItem("token", req['token']);
                set_view("profileview");
                establishWebSocket();
                load_stored_stats();
                load_information();
                load_charts();
            }
        }
    };
    xhttp.open("POST", "/sign_in", true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(f));
};



function signup_form_request(formData)
{
    var fname = formData.signup_first_name.value;
    var lname = formData.signup_family_name.value;
    var gender = formData.signup_gender.value;
    var city = formData.signup_City.value;
    var country = formData.signup_Country.value;
    var email = formData.signup_Email.value;
    var password = formData.signup_Password.value;
    var reppassword = formData.signup_RepPassword.value;

    if (password == reppassword)
    {
        document.getElementById("password_error").innerHTML = "";
        var f = { email: email, password: password, firstname: fname, familyname: lname, gender: gender, city: city, country: country};

        var req;
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4) {
                req = JSON.parse(this.responseText);
                document.getElementById("password_error").innerHTML = req['message'];
            }
        };
        xhttp.open("POST", "/sign_up", true);
        xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhttp.send(JSON.stringify(f));
    }
    else
    {
        document.getElementById("password_error").innerHTML = "Passwords are not matching!";
    }
};


function openPage(evt, pageName)
{
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    document.getElementById(pageName).style.display = "block";
    evt.currentTarget.className += " active";
}


function change_pass(formData)
{

    var newPass1 = formData.new_Password.value;
    var newPass2 = formData.new_RepPassword.value;
    if (newPass1 == newPass2)
    {
        var oldPass = formData.old_Password.value;
        var token = localStorage.getItem("token");
            
        var f = {"oldpassword": oldPass, "newpassword": newPass1};
        var req;
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4) {
                req = JSON.parse(this.responseText);
                document.getElementById("change_pass_message").innerHTML = req['message'];
            }
        };
        xhttp.open("PUT", "/change_password", true);
        xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhttp.setRequestHeader("token", token);
        xhttp.send(JSON.stringify(f));
    }
    else
    {
        document.getElementById("change_pass_message").innerHTML = "Passwords not matching";
    }
}


function log_out()
{
    var token = localStorage.getItem("token");

    var req;
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            req = JSON.parse(this.responseText);

            try{
                document.getElementById("log_out_message").innerHTML = req['message'];
            }catch{}
            localStorage.removeItem("token");
            set_view("welcomeview");
        }
    };
    xhttp.open("DELETE", "/sign_out", true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.setRequestHeader("token", token);
    xhttp.send();
}


function load_information()
{
    var token = localStorage.getItem("token");

    var info
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            info = JSON.parse(this.responseText);

            if (info['pass']){
                if ('UserData' in info){
                document.getElementById("info_first_name").innerHTML = "<b>First name: </b>" + info['UserData']['FirstName'];
                document.getElementById("info_family_name").innerHTML = "<b>Family name: </b> " + info['UserData']['FamilyName'];
                document.getElementById("info_gender").innerHTML = "<b>Gender: </b> " + info['UserData']['Gender'];
                document.getElementById("info_city").innerHTML = "<b>City: </b> " + info['UserData']['City'];
                document.getElementById("info_country").innerHTML = "<b>Country: </b> " + info['UserData']['Country'];
                document.getElementById("info_email").innerHTML = "<b>Email: </b> " + info['UserData']['Email'];
                refresh_wall();
                }
            }
        }
    };
    xhttp.open("GET", "/get_user_data_by_token", true);
    xhttp.setRequestHeader("Content-Type", "charset=UTF-8");
    xhttp.setRequestHeader("token", token);
    xhttp.send();
}


function postMessage(token, content, email, browse)
{
    var xhttp = new XMLHttpRequest();
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
        var f = {"email": email, "message": content, "latitude": position.coords.latitude,
                "longitude": position.coords.longitude};
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4) {
                var info = JSON.parse(this.responseText);
                if (info['pass'])
                {
                    if(browse)
                    {
                        refresh_wall_email(email)
                    }
                    else{
                        refresh_wall();
                    }
                }
            }
        };
        xhttp.open("POST", "/post_message", true);
        xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhttp.setRequestHeader("token", token);
        xhttp.send(JSON.stringify(f));
        })
    }
}

function submit_message(formData)
{
    var token = localStorage.getItem("token");
    var content = formData.submit_field.value;

    var info
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            info = JSON.parse(this.responseText);
            email = info['UserData']['Email']

            if (content){
                postMessage(token, content, email, false);
                formData.submit_field.value = ""
            }
        }
    };
    xhttp.open("GET", "/get_user_data_by_token", true);
    xhttp.setRequestHeader("Content-Type", "charset=UTF-8");
    xhttp.setRequestHeader("token", token);
    xhttp.send();
}

function submit_message_b(formData) {
    var token = localStorage.getItem("token");
    var content = formData.submit_field_b.value;
    var email = document.getElementById("search_name").value;

    if (content){
        postMessage(token, content, email, true);
        formData.submit_field_b.value = ""
    }
}

function refresh_wall(){
    var token = localStorage.getItem("token");
    
    var info
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            info = JSON.parse(this.responseText);
            if (info['pass'])
            {
                var wall = document.getElementById("Personal_wall");
                wall.innerHTML = "";
                for (var i = info['messages'].length - 1; i >= 0; i--)
                {
                    var message_div = document.createElement("div");
                    var header = document.createElement("h3");
                    header.innerHTML = info['messages'][i]['Sender'];
                    var message = document.createElement("p");
                    var location = document.createElement("p");
                    location.innerHTML = info['messages'][i]['City'] + ", " + info['messages'][i]['Country'];
                    location.setAttribute("style", "text-align:right; font-size:14px; color:gray; margin-top:0px;");
                    message.innerHTML = info['messages'][i]['Message'];
                    message_div.appendChild(header);
                    message_div.appendChild(message);
                    message_div.appendChild(location);
                    wall.appendChild(message_div);
                }
            }
        }
    };
    xhttp.open("GET", "/get_user_messages_by_token", true);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.setRequestHeader("token", token);
    xhttp.send();
}

function search_user(formData)
{
    var token = localStorage.getItem("token");
    var user_email = formData.search_name.value;
    
    var f = "?email=" + user_email
    var info
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            info = JSON.parse(this.responseText);
                
            if (info['pass'])
            {
                document.getElementById("search_error").innerHTML = "";
                document.getElementById("browse_user").style.display = "block";
                    
                document.getElementById("info_b_first_name").innerHTML = "<b>First name: </b>" + info['UserData']['FirstName'];
                document.getElementById("info_b_family_name").innerHTML =  "<b>Family name: </b> " + info['UserData']['FamilyName'];
                document.getElementById("info_b_gender").innerHTML =  "<b>Gender: </b> " + info['UserData']['Gender'];
                document.getElementById("info_b_city").innerHTML =  "<b>City: </b> " + info['UserData']['City'];
                document.getElementById("info_b_country").innerHTML =  "<b>Country: </b> " + info['UserData']['Country'];
                document.getElementById("info_b_email").innerHTML =  "<b>Email: </b> " + info['UserData']['Email'];
                refresh_wall_email(user_email);
            }
            else
            {
                document.getElementById("search_error").innerHTML = info.message;
            }

        }
    };
    xhttp.open("GET", "/get_user_data_by_email" + f, true);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.setRequestHeader("token", token);
    xhttp.send();
}


function refresh_wall_email(email) {
    var token = localStorage.getItem("token");
    if (email == null)
    {
        email = document.getElementById("search_name").value;
    }

    var f = "?email=" + email
    var info
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            info = JSON.parse(this.responseText);
                
            if (info['pass']){
                var wall = document.getElementById("Personal_wall_b");
                wall.innerHTML = "";
                for (var i = info['messages'].length - 1; i >= 0; i--)
                {
                    var message_div = document.createElement("div");
                    var header = document.createElement("h3");
                    header.innerHTML = info['messages'][i]['Sender'];
                    var message = document.createElement("p");
                    var location = document.createElement("p");
                    location.innerHTML = info['messages'][i]['City'] + ", " + info['messages'][i]['Country'];
                    location.setAttribute("style", "text-align:right; font-size:14px; color:gray; margin-top:0px;");
                    message.innerHTML = info['messages'][i]['Message'];
                    message_div.appendChild(header);
                    message_div.appendChild(message);
                    message_div.appendChild(location);
                    wall.appendChild(message_div);
                }
            }
            else
            {
                document.getElementById("search_error").innerHTML = req.message;
            }
        }
    };
    xhttp.open("GET", "/get_user_messages_by_email" + f, true);
    xhttp.setRequestHeader("Content-Type", "charset=UTF-8");
    xhttp.setRequestHeader("token", token);
    xhttp.send();
}



function load_stored_stats(){
    update_people_online(localStorage.getItem("TotalNumPeopleOnline"))
    update_num_accounts(localStorage.getItem("TotalNumUsers"))
    update_num_posts(localStorage.getItem("TotalNumPosts"))
}


function update_people_online(newNumber){
    if(newNumber != null){
        localStorage.setItem("numPeopleOnline", newNumber);
        document.getElementById('stats_online').innerHTML = newNumber;
    }
}

function update_num_accounts(newNumber){
    if(newNumber != null){
        localStorage.setItem("TotalNumUsers", newNumber);
        document.getElementById('stats_accounts').innerHTML = newNumber;
    }
}

function update_num_posts(newNumber){
    if(newNumber != null){
        localStorage.setItem("TotalNumPosts", newNumber);
        document.getElementById('stats_posts').innerHTML = newNumber;
    }
}

function changeStat(pageName)
{
    var canvaslink;
    canvaslink = document.getElementsByClassName("canvaslink");
    for (i = 0; i < canvaslink.length; i++) {
        canvaslink[i].style.display = "none";
    }

    document.getElementById(pageName).style.display = "block";
}