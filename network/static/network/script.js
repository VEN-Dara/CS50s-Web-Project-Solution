const fetchJSON = async (url, options) => {
    const response = await fetch(url, options);
    return response.json();
}

const navigateTo = url => {
    history.pushState(null, null, url);
    router();
};

const newFeed = () => {
    const url = "/post/new_feed";
    document.querySelector("#post-container").style.display = "block";
    document.querySelector(".header-container").style.display = "none";
    document.querySelector('#text-post').value = "";
    loadPost(url);
}

const loadPost = async (url, pagination=1) => {
    const container = document.querySelector(".container-fluid");
    const username = document.querySelector('#profile').dataset.username;
    container.innerHTML = "";
    console.log(pagination);
    options = (pagination !== 1) ? {
        method: "POST",
        body: JSON.stringify({ page_num: pagination })
    } : {}
    
    try {
        const data = await fetchJSON(url, options);

        pagination = (pagination >= data.posts_length) ? data.posts_length : pagination;
        pagination = (pagination <= 1) ? 1 : pagination;
        console.log(pagination);

        data.posts.forEach(post => {
            const isLoveStatus = isLove(username, post.reactions);
            const element = document.createElement('div');
            element.className = "card";
            element.innerHTML = `
                <div class="card-body">
                    <div class="d-flex align-middle">
                        <a href="profile?username=${post.user}" data-link>
                            <h5 class="card-title m-0">${post.user}</h5>
                        </a> 
                        ` 
                        + loadEditPost(username, post.user, post.body, post.id) +
                        `
                    </div>
                    <p class="card-text">${post.body}</p>
                    <p class="card-subtitle mb-2 text-muted">${post.date}</p>
                    <div class="d-flex align-items-center">
                    <button class="love-btn-style" id="love-btn-${post.id}" data-post-id="${post.id}" data-value="${isLoveStatus ? 'unlove' : 'love'}">${isLoveStatus ? '<i class="bi bi-heart-fill"></i>' : '<i class="bi bi-heart"></i>'}</button>
                    <span id="reaction-amount-${post.id}">${post.reactions.length}</span>
                    </div>
                    <p> Comment </p>
                </div>
            `
            container.appendChild(element);
        })

        let paginatorElement = ``;
        for(let i=1; i<=data.posts_length; i++) {
            paginatorElement += `
            <li class="page-item"><a class="page-link paginator" id="paginator-${i}" data-value="${i}">${i}</a></li>
            `;
        }

        const postPagination = document.createElement('div');
        postPagination.className = "post-pagination";
        postPagination.innerHTML = `
            <nav aria-label="Page navigation example">
                <ul class="pagination">
                    <li class="page-item">
                        <a class="page-link paginator" id="previousPagination" data-value="${pagination-1}" aria-label="Previous">
                        <span aria-hidden="true">&laquo;</span>
                        </a>
                    </li>` + paginatorElement + `
                    <li class="page-item">
                        <a class="page-link paginator" id="nextPagination" data-value="${pagination+1}" aria-label="Next">
                        <span aria-hidden="true">&raquo;</span>
                        </a>
                    </li>
                </ul>
            </nav>
        `;
        container.appendChild(postPagination);

        //Active pagination
        document.querySelector(`#paginator-${pagination}`).parentElement.classList.add("active");

        const nextPag = document.querySelector('#nextPagination');
        const previousPag = document.querySelector('#previousPagination');

        nextPag.classList.remove("disabled");
        previousPag.classList.remove("disabled");

        if(pagination===data.posts_length) {    
            nextPag.classList.add("disabled");
        }
        if(pagination===1) {
            previousPag.classList.add("disabled");
        }

    } catch (error) {
        console.error("Error loading post", error);
    }
}

const isLove = (username, reactions) => {
    return reactions.some(reaction => reaction.username === username);
}

const loadEditPost = (username, postUsername, bodyPost, postID) => {
    if(username === postUsername) {
        return `
            <!-- Button trigger modal -->
            <button type="button" class="bg-white border-0 btn-sm text-primary" data-bs-toggle="modal" data-bs-target="#edit-post-form-${postID}">
                <i class="bi bi-pencil-square"></i>
                Edit
            </button>
            
            <!-- Modal -->
            <div class="modal fade" id="edit-post-form-${postID}" tabindex="-1" aria-labelledby="edit-post-formLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="edit-post-formLabel">Edit Post</h5>
                            <button type="button" class="btn-close" style="line-height: 1;" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="form-floating">
                                <textarea class="form-control" placeholder="Leave a comment here" id="edit-post-body" style="height: 100px" data-post-id="${postID}">${bodyPost}</textarea>
                                <label for="edit-post-body">Leave something here</label>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" id="cancel-edit-post-btn" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="submit-edit-post-btn">Save</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    return '';
}

const post = async event => {
    event.preventDefault();
    const body = document.querySelector('#text-post').value;

    try {
        await fetch('/post', {
            method: 'POST',
            body: JSON.stringify({ body })
        });
        document.querySelector('#text-post').value = "";
        loadPost("/post/new_feed");
    } catch (error) {
        console.error("Error post is not success", error);
    }
}

const loadProfileInfo = async username => {

    try {
        const user = await fetchJSON(`profile/${username}`);
        const profileName = document.querySelector('#profile').dataset.username;
        const isFollowed = user.followers.some(follower => follower.username === profileName)
    
        let follow_btn_class = (username===profileName) ? "d-none " : "d-block " ;
        follow_btn_class += !isFollowed ? "btn-dark " : "btn-outline-dark " ;
        let follow_btn_label = isFollowed ? "Unfollow" : "Follow";
    
        const header = document.querySelector(".header-container");
        header.innerHTML = `
            <h5>${username.charAt(0).toUpperCase() + username.slice(1)}</h5>
            <button class="btn ${follow_btn_class}" id="follow-btn" value="${isFollowed}">${follow_btn_label}</button>
            <div class="d-flex justify-content-around mb-2">
                <div>
                    <strong>Follower:</strong> <span>${user.followers.length}</span>
                </div>
                <div>
                    <strong>Following:</strong> <span>${user.followings.length}</span>
                </div>
            </div>
        `;
    } catch (error) {
        console.error("Error post is not success", error);
    }

}

const loadProfile = () => {
    const urlObj = new URL(location.href);
    const username = urlObj.searchParams.get("username");

    document.querySelector("#post-container").style.display = "none";
    document.querySelector(".header-container").style.display = "block";

    loadProfileInfo(username);
    loadPost(`/post/${username}`);
}

const follow = async button => {
    const urlObj = new URL(location.href);
    const username = urlObj.searchParams.get("username");
    const isFollowing = button.value === "false";
    
    try {
        await fetch(`profile/${username}`, {
            method: 'PUT',
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ isFollowing })
        });
        loadProfileInfo(username);
    } catch (error) {
        console.error("Error follow is not success", error);
    }

};

const loadFollowPage = () => {
    const postContainer = document.querySelector('#post-container');
    const headerContainer = document.querySelector('.header-container');
    const bodyContainer = document.querySelector('.container-fluid');

    postContainer.style.display = "none";
    headerContainer.style.display = "none";
    bodyContainer.style.display = "block";

    loadPost('post/following');
}
const router = async () => {
    const routes = [
        { path: "/", view: newFeed },
        { path: "/profile", view: loadProfile },
        { path: "/following", view: loadFollowPage }
    ]

    const matchingRoute = routes.find(route => route.path === location.pathname);
    console.log(matchingRoute);
    matchingRoute.view();
}

const performTask = btnTarget => {
    const buttons = [
        {id : "follow-btn", handle: follow},
        {id : "submit-edit-post-btn", handle: editPost},
        {id : `love-btn-${btnTarget.dataset.postId || 0}`, handle: reactPost}

    ]

    const matchingButton = buttons.find(button => button.id === btnTarget.id);
    if (matchingButton) {
        matchingButton.handle(btnTarget);
    }
}

const loadPaginator = async paginatorValue => {
    
    const routes = [
        {path: "/", url:"/post/new_feed"},
        {path: "/following", url:"/post/following"},
        {path: "/profile", url:`/post/${new URLSearchParams(window.location.search).get('username')}`}
    ]

    const matchingRoute = routes.find(route => route.path === location.pathname);
    loadPost(matchingRoute.url, parseInt(paginatorValue));
}

const editPost = async (saveBtn) => {
    const post = document.querySelector("#edit-post-body");
    const body = post.value;
    const id = parseInt(post.dataset.postId);
    console.log(id)
    console.log(body)

    if(body === "") {
        alert("Text something in caption..");
        post.setAttribute("autofocus", true);
    }
    else {
        await fetch('/post', {
            method: "PUT",
            body: JSON.stringify({
                body,
                id
            })
        })
        .then(() => {
            document.querySelector("#cancel-edit-post-btn").click();
            navigateTo(location.href);
        })
        .catch(error => {
            console.error("Error", error);
        })
    }
}

const reactPost = async (loveBtn) => {
    const id = loveBtn.dataset.postId;
    const reaction = loveBtn.dataset.value;
    
    await fetch("/post", {
        method: "PUT",
        body: JSON.stringify({
            id,
            reaction
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.post);
        loveBtn.innerHTML = (reaction === 'love') ? '<i class="bi bi-heart-fill"></i>' : '<i class="bi bi-heart"></i>'
        loveBtn.setAttribute("data-value", (reaction === 'love') ? "unlove" : "love")
        document.querySelector(`#reaction-amount-${id}`).textContent = data.post.reactions.length;
    })
    .catch(error => {
        console.error("Reaction error", error);
    })

}

window.addEventListener("popstate", router);

document.addEventListener('DOMContentLoaded', () => {
    document.body.addEventListener("click", e => {
        const link = e.target.closest("[data-link]");
        const button = e.target.closest("button");
        const paginator = e.target.closest(".paginator");

        if (link) {
            e.preventDefault();
            navigateTo(link.href);
        } else if (button && button.parentElement.tagName.toLowerCase() !== "form") {
            e.preventDefault();
            performTask(button);
            console.log(button)
        }
        else if(paginator) {
            e.preventDefault();
            loadPaginator(paginator.dataset.value);
        }
    });

    router();

    //Add new post
    document.querySelector('.post').addEventListener("submit", post);
    
})


