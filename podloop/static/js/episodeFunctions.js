//variables
dataBackEnd = {};
followers_count = document.getElementById("followers");
follow_section = document.getElementById("follow_section");
like_button = document.getElementById("like_button");
like_count = document.getElementById("like_count");
form_comment = document.getElementById("post_comment_form");
form_reply = document.getElementById("post_reply_form");
comment_section = document.getElementById("comments");
success_alert = document.getElementById("success_alert");
comments_count = document.getElementById("comments_count");
modal = document.getElementById("reply_modal");
//listeners
form_comment.addEventListener("submit", function (event) {
  event.preventDefault();
  var comment_value = document.getElementById("comment").value;
  comment(comment_value, false, 0);
});
form_reply.addEventListener("submit", function (event) {
  event.preventDefault();
  var comment_value = document.getElementById("reply").value;
  var parent_id = document.getElementById("parent_comment").value;
  comment(comment_value, true, parent_id);
});

async function call_api_post(api_url, data) {
  var jsonObject = {};
  Object.entries(data).forEach(([key, value]) => {
    jsonObject[key] = value;
  });
  await fetch(api_url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": data["csrfmiddlewaretoken"],
    },
    body: JSON.stringify(jsonObject),
  })
    .then(function (response) {
      if (response.ok) {
        return response.text();
      }
      throw new Error("Network response was not ok.");
    })
    .then(function (data) {})
    .catch(function (error) {
      console.log("Error:", error.message);
    });
}
async function call_api_get(api_url) {
  await fetch(api_url)
    .then(function (response) {
      if (response.ok) {
        return response.json();
      }
      throw new Error("Network response was not ok.");
    })
    .then(function (data) {
      Object.entries(data).forEach(([key, value]) => {
        dataBackEnd[key] = value;
      });
    })
    .catch(function (error) {
      console.log("Error:", error.message);
    });
}

async function check_auth() {
  var api_url = "http://127.0.0.1:8000/api/is-authenticated";
  await call_api_get(api_url);
}

async function get_episode_user_info() {
  var api_url = `http://127.0.0.1:8000/api/podcasts/${dataBackEnd["podcast_slug"]}/episode/${dataBackEnd["episode_slug"]}`;
  await call_api_get(api_url);
}

async function toggle_follow() {
  var api_url = `http://127.0.0.1:8000/api/podcasts/${dataBackEnd["podcast_slug"]}/toggle-follow`;
  await call_api_get(api_url);
  await get_episode_user_info();
  setPage();
}

async function toggle_like_episode() {
  var api_url = `http://127.0.0.1:8000/api/podcasts/${dataBackEnd["podcast_slug"]}/episode/${dataBackEnd["episode_slug"]}/toggle-like`;
  await call_api_get(api_url);
  await get_episode_user_info();
  setPage();
}

async function sort_comments(sort_by) {
  var api_url = `http://127.0.0.1:8000/api/podcasts/${dataBackEnd["podcast_slug"]}/episode/${dataBackEnd["episode_slug"]}/get-comments?sort_by=${sort_by}`;
  await call_api_get(api_url);
  setCommentSection();
}

async function get_comments() {
  var api_url = `http://127.0.0.1:8000/api/podcasts/${dataBackEnd["podcast_slug"]}/episode/${dataBackEnd["episode_slug"]}/get-comments`;
  await call_api_get(api_url);
  setCommentSection();
}

async function comment(comment, is_reply, reply_to) {
  var api_url = `http://127.0.0.1:8000/api/podcasts/${dataBackEnd["podcast_slug"]}/episode/${dataBackEnd["episode_slug"]}/post-comment`;

  var data = {};
  var comment = "";
  var csrf_token = "";

  if (is_reply) {
    comment = document.getElementById("reply").value;
    csrf_token = document.querySelector(
      "#post_comment_form input[name='csrfmiddlewaretoken']"
    ).value;
  } else {
    comment = document.getElementById("comment").value;
    csrf_token = document.querySelector(
      "#post_reply_form input[name='csrfmiddlewaretoken']"
    ).value;
  }
  data["comment"] = comment;
  data["csrfmiddlewaretoken"] = csrf_token;
  data["is_reply"] = is_reply;
  data["reply_to"] = reply_to;
  await call_api_post(api_url, data);
  await sort_comments(dataBackEnd["sort_by"]);
  $(modal).modal("hide");
  success_alert.innerHTML = `
  <div
      class="alert alert-success alert-dismissible fade show"
      role="alert"
    >
      <strong>Comment created!</strong>
      <button
        type="button"
        class="btn-close"
        data-bs-dismiss="alert"
        aria-label="Close"
      ></button>
    </div>
  `;
}

function reply_comment(id_parent_comment, reply_to) {
  $(modal).modal("show");
  document.getElementById("reply_header").innerHTML = "Reply to " + reply_to;
  document.getElementById("parent_comment").value = id_parent_comment;
}

async function delete_comment(id) {
  var api_url = `http://127.0.0.1:8000/api/comment/${id}/delete`;
  await call_api_get(api_url);
  await sort_comments(dataBackEnd["sort_by"]);
}

async function toggle_like_comment(id) {
  var api_url = `http://127.0.0.1:8000/api/comment/${id}/toggle-like`;
  await call_api_get(api_url);
  await sort_comments(dataBackEnd["sort_by"]);
}

async function init(dataFrontEnd) {
  dataBackEnd = dataFrontEnd;
  dataBackEnd["is_authenticated"] = false;
  //I get all the data that i need from the frontend
  await check_auth();
  //i check if the user is authenticated
  await get_episode_user_info();
  await get_comments();
  //in both cases i display what is necessary
  setPage();
}

function comment_template(
  id,
  username,
  is_owner,
  profile_picture,
  date,
  text,
  can_reply,
  is_liked,
  likes,
  reply_to,
  parent_id
) {
  result = `
  <div class="container mt-3">
        <div class="row d-flex">
          <div class="col-md-11 col-lg-9 col-xl-7">
            <div class="d-flex flex-start mb-2">
              <img
                class="rounded-circle shadow-1-strong me-3"
                src="${profile_picture}"
                alt="avatar"
                width="35"
                height="35"
              />
              <div class="card w-100 bg-dark">
                <div class="card-body p-1 text-light">
                  <div class="">
                    <h6 class="text-warning">${username} <span class="small text-light">${date}</span></h6>
                    <p style="font-size: 14px">
                     ${text}
                    </p>

                    <div
                      class="d-flex justify-content-between align-items-center"
                    >
                      <div class="d-flex align-items-center">
                        <p class="mb-0">
                          <i class="bi bi-hand-thumbs-up-fill ${
                            is_liked ? "text-success" : "text-light"
                          }" onClick="toggle_like_comment(${id})" style="cursor:pointer;"></i>
                          <small>${likes}</small>
                        </p>
                      </div>
                      ${
                        can_reply
                          ? `<p class="text-light mb-0" style="cursor:pointer;" onClick="reply_comment('${parent_id}','${reply_to}')"><i class="bi bi-reply-fill"></i> Reply</p>`
                          : ""
                      }
                      ${
                        is_owner
                          ? `<p class="text-danger mb-0" style="cursor:pointer;" onClick="delete_comment(${id})">Delete</p>`
                          : ""
                      }
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
  `;
  return result;
}
function setPage() {
  like_element = "";

  if (dataBackEnd["is_authenticated"]) {
    if (dataBackEnd["is_owner"]) {
      follow_element = `<a class="btn btn-sm btn-warning" href="#">Edit</a>`;
    } else if (dataBackEnd["is_following"]) {
      follow_element = `<a class="btn btn-sm btn-danger" href="#" onClick=toggle_follow()>Unfollow</a>`;
    } else {
      follow_element = `<a class="btn btn-sm btn-success" href="#" onClick=toggle_follow()>follow</a>`;
    }

    if (dataBackEnd["is_liked"]) {
      like_element = `<i class="bi bi-hand-thumbs-up-fill text-success" style="cursor:pointer;" onClick=toggle_like_episode()></i>`;
    } else {
      like_element = `<i class="bi bi-hand-thumbs-up-fill text-light" style="cursor:pointer;" onClick=toggle_like_episode()></i>`;
    }
  } else {
    like_element = `<i class="bi bi-hand-thumbs-up-fill" disabled></i>`;
    follow_element = `<a class="btn btn-sm btn-warning" href="/login">Login</a>`;
  }
  followers_count.innerHTML = dataBackEnd["followers"] + " Followers";
  like_button.innerHTML = like_element;
  follow_section.innerHTML = follow_element;
  like_count.innerHTML = dataBackEnd["likes"];
}

function setCommentSection() {
  comment_section.innerHTML = "";
  sort_by = dataBackEnd["sort_by"];
  comments_html = `<div class="dropdown bg-dark d-flex justify-content-end">
  <button
    class="btn btn-secondary dropdown-toggle"
    type="button"
    data-bs-toggle="dropdown"
    aria-expanded="false"
  >
    Sort By
  </button>
  <ul class="dropdown-menu dropdown-menu-dark">
    <li>
      <p
        class="dropdown-item ${sort_by == "old_to_new" ? "active" : ""}"
        onClick=sort_comments("old_to_new")
        >Old to new</p
      >
    </li>
    <li>
      <p
        class="dropdown-item ${sort_by == "new_to_old" ? "active" : ""}"
        onClick=sort_comments("new_to_old")
        >New to old</p
      >
    </li>
  </ul>
</div>
  `;
  //at first the total length is the number of top level comments
  total_comments_count = dataBackEnd["comments"].length;
  if (dataBackEnd["comments"].length > 0) {
    dataBackEnd["comments"].forEach((entry) => {
      comments_html += comment_template(
        entry.comment.id,
        entry.comment.owner,
        entry.comment.is_owner,
        entry.comment.link_profile_picture,
        entry.comment.date,
        entry.comment.text,
        true,
        entry.comment.is_liked,
        entry.comment.likes,
        entry.comment.owner,
        entry.comment.id
      );
      if (entry.replies.length > 0) {
        comments_html += `<a class="text-light ms-5 mb-3 text-decoration-none" data-bs-toggle="collapse" href="#collapse${entry.comment.id}" role="button" aria-expanded="false" aria-controls="collapse${entry.comment.id}">
          Show replies
        </a>`;
      }
      comments_html += `
      <div class="collapse" id="collapse${entry.comment.id}">
      <div class="replies ms-5">
      `;
      //then we add all the replies for each comment
      total_comments_count += entry.replies.length;
      entry.replies.forEach((reply) => {
        comments_html += comment_template(
          reply.id,
          reply.owner,
          reply.is_owner,
          reply.link_profile_picture,
          reply.date,
          reply.text,
          false,
          reply.is_liked,
          reply.likes,
          null,
          null
        );
      });
      comments_html += `
      </div>
      </div>
      `;
    });
  }
  comment_section.innerHTML = comments_html;
  comments_count.innerHTML = total_comments_count;
}
