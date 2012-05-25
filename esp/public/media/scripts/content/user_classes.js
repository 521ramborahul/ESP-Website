function update_user_classes() {
  if (esp_user.cur_admin == "1") {
    $j(".admin").removeClass("hidden");
  }
  if (esp_user.cur_retTitle) {
    $j(".unmorph").removeClass("hidden");
    document.getElementById("unmorph_text").innerHTML = "Click above to return to your administrator account - " + esp_user.cur_retTitle;
  }
  if (esp_user.cur_qsd_bits == "1") {
    $j(".qsd_bits").removeClass("hidden");
  }
  if (esp_user.cur_username != null) {
    $j(".not_logged_in").addClass("hidden");
    $j(".logged_in").removeClass("hidden");
  }
  else {
    $j(".not_logged_in").removeClass("hidden");
    $j(".logged_in").addClass("hidden");
  }

  var type_name = '';
  var hidden_name = '';
  for (var i = 0; i < esp_user.cur_roles.length; i++) {
    type_name = "." + esp_user.cur_roles[i];
    $j(type_name).removeClass("hidden");
  }
  
  //    Write user's name in the appropriate spot in the login box
  $j("#loginbox_user_name").html("Hello, " + esp_user.cur_first_name + " " + esp_user.cur_last_name + "!");
}
