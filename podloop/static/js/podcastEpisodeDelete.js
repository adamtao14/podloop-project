dataBackEnd = {};
delete_podcast_form = document.getElementById("confirm_delete_podcast");
delete_episode_form = document.getElementById("confirm_delete_episode");

if(delete_podcast_form){
  delete_podcast_form.addEventListener("submit", async function(event){
      event.preventDefault();
      await delete_podcast();
  });
}
if(delete_episode_form){

  delete_episode_form.addEventListener("submit", async function(event){
      event.preventDefault();
      await delete_episode();
  });
}

//delete type tells me if i'm doing a delete of a podcast (1) or and episode (0)
async function call_api_post(api_url, data, delete_type) {
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
          //redirect to /creator
          if (delete_type == 1){
            window.location.href = "/profile/creator?delete_success='Podcast deleted successfully'";
          }else{
            window.location.href = `/podcasts/${dataBackEnd["podcast_slug"]}?delete_success='Episode deleted successfully'`;
          }
        }
        throw new Error("Network response was not ok.");
      })
      .then(function (data) {})
      .catch(function (error) {
        console.log("Error:", error.message);
      });
  }

async function delete_podcast(){
    var api_url = `http://127.0.0.1:8000/api/podcasts/${dataBackEnd["podcast_slug"]}/delete`;
    csrf_token = document.querySelector("#confirm_delete_podcast input[name='csrfmiddlewaretoken']").value;
    data = {};
    data["csrfmiddlewaretoken"] = csrf_token;
    await call_api_post(api_url, data, 1);

}
async function delete_episode(){
    var api_url = `http://127.0.0.1:8000/api/podcasts/${dataBackEnd["podcast_slug"]}/episode/${dataBackEnd["episode_slug"]}/delete`;
    csrf_token = document.querySelector("#confirm_delete_episode input[name='csrfmiddlewaretoken']").value;
    data = {};
    data["csrfmiddlewaretoken"] = csrf_token;
    await call_api_post(api_url, data, 0);

}

function init(dataFrontend){
    dataBackEnd = dataFrontend;
}