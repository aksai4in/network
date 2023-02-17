document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector("#login") === null) {
        if (window.location.pathname.slice(1, 8) === "profile") {
            return profile_posts(window.location.pathname.slice(9,))
        }
        else if (window.location.pathname.slice(1, 10) === "following") {
            return following_posts(window.location.pathname.slice(11,))
        }
        else if (window.location.pathname === "/") {
            return all_posts();
        }
    }
});
function all_posts(){
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    fetch(`/posts/${urlParams.get('page')}`)
        .then(response => response.json())
        .then(data => {
            data[0].forEach(post => add_post(post, data[1]));
            console.log(data);
        });
    document.querySelector("#newpost").onsubmit = () => {
        fetch("/posts", {
            method: "POST",
            body: JSON.stringify({
                user: document.querySelector('#username').innerHTML,
                content: document.querySelector("#textarea").value
            })
        })
            .then(response => response.json())
            .then(res => {
                console.log(res["message"]);
                document.querySelector("#textarea").value = "";
                document.querySelector(".posts").innerHTML = "";
                all_posts();
            });
        return false;
    }
}
function following_posts(username){
    fetch(`/following/${username}`, {
        method: "POST"
    })
        .then(response => response.json())
        .then(data => {
            data[0].forEach(post => add_post(post,data[1]));
            console.log(data);
        });
}
function profile_posts(username){
    followers(username);
    //create follow and unfollow buttons
    const user = document.querySelector("#username").innerHTML;
    if(document.querySelector("#follow") != null){
        document.querySelector("#follow").addEventListener('click', () => {
            fetch(`${username}`, {
                method: "POST",
                body: JSON.stringify({
                    user: user,
                    follow: true
                })
            })
                .then(response => response.json())
                .then(data => console.log(data))
                .then(() => {
                    return followers(username)
                })
        })
        document.querySelector("#unfollow").addEventListener('click', () => {
            fetch(`${username}`, {
                method: "POST",
                body: JSON.stringify({
                    user: user,
                    follow: false
                })
            })
                .then(response => response.json())
                .then(data => console.log(data))
                .then(() => {
                    return followers(username)
                })
        })
    }
    
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    //load all profile posts
    fetch(`/profilePosts/${username}/${urlParams.get('page')}`)
        .then(response => response.json())
        .then(data => {
            data[0].forEach(post => add_post(post, data[1]));
            console.log(data);
        });
    
}
function followers(username){
    fetch(`/profilePosts/${username}/1`, {
        method: "POST",
    })
    .then(response => response.json())
    .then(data => {
        document.querySelector("#following").innerHTML = data["following"];
        document.querySelector("#followers").innerHTML = data["followers"];
    });
}
function add_post(post, likedPosts) {
    const username = document.querySelector("#username").innerHTML;
    const div = document.createElement('div');
    const p = document.createElement('p');
    const user = document.createElement('a');
    user.href = `/profile/${post.username}`;
    p.append(user);
    const content = document.createElement('p');
    content.id = `content${post.id}`;
    const timestamp = document.createElement('p');
    const likes = document.createElement('p');
    const like = document.createElement('button');
    if(likedPosts.includes(post.id)){
        like.textContent = "Liked";
    }
    else{
        like.textContent = "Like";
    }
    like.className = "btn btn-success btn-sm";
    likes.id = `likes${post.id}`
    like.addEventListener('click', () => {like_post(username, post.id, like)});
    user.textContent = post.username;
    user.id = "user";
    content.textContent = post.content;
    timestamp.textContent = post.timestamp;
    likes.textContent = post.likes;
    div.className = "post";
    div.appendChild(p);
    div.appendChild(content);
    div.appendChild(timestamp);
    div.appendChild(likes);
    div.appendChild(like);
    if(username === post.username){
        const edit = document.createElement('button');
        edit.textContent = "Edit";
        edit.className = "btn btn-primary btn-sm";
        const save = document.createElement('button');
        save.textContent = "Save";
        save.className = "btn btn-danger btn-sm";
        save.addEventListener('click', () => {save_post(post.id, div, save, edit)});
        edit.addEventListener('click', () => {edit_post(post.id, div, edit, save)});
        div.appendChild(edit);
    }
    document.querySelector(".posts").append(div);
}
function like_post(username, postId, like){
    fetch("/posts", {
        method: "POST",
        body: JSON.stringify({
            post_id: postId,
            user: username,
            like: true
        })
    })
    .then(response => response.json())
    .then(res => {
        console.log(res["message"]);
        const likes = document.querySelector(`#likes${postId}`);
        likes.textContent = res["likes"];
        if(like.textContent == "Like"){
            like.textContent = "Liked";
        }else{
            like.textContent = "Like";
        }
    });
}
function edit_post(postId, div, edit, save){
    div.removeChild(edit);
    div.appendChild(save);
    const content = document.getElementById(`content${postId}`);
    const text = document.createElement('input');
    text.id = `edited${postId}`;
    text.type = "text";
    text.value = `${content.textContent}`
    console.log(postId);
    div.insertBefore(text, content);
    div.removeChild(content);
}
function save_post(postId, div, save, edit){
    div.removeChild(save);
    div.appendChild(edit);
    const text = document.getElementById(`edited${postId}`);
    fetch("/posts", {
        method: "POST",
        body: JSON.stringify({
            post_id: postId,
            user: document.querySelector('#username').innerHTML,
            content: text.value
        })
    })
    .then(response => response.json())
    .then(res => console.log(res));
    const content = document.createElement('p');
    content.textContent = text.value;
    content.id = `content${postId}`;
    div.insertBefore(content, text);
    div.removeChild(text);  
}