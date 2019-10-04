/* Project specific Javascript goes here. */

/*
Formatting hack to get around crispy-forms unfortunate hardcoding
in helpers.FormHelper:

    if template_pack == 'bootstrap4':
        grid_colum_matcher = re.compile('\w*col-(xs|sm|md|lg|xl)-\d+\w*')
        using_grid_layout = (grid_colum_matcher.match(self.label_class) or
                             grid_colum_matcher.match(self.field_class))
        if using_grid_layout:
            items['using_grid_layout'] = True

Issues with the above approach:

1. Fragile: Assumes Bootstrap 4's API doesn't change (it does)
2. Unforgiving: Doesn't allow for any variation in template design
3. Really Unforgiving: No way to override this behavior
4. Undocumented: No mention in the documentation, or it's too hard for me to find
*/
$('.form-group').removeClass('row');

/* Notifications JS basic client */
$(function () {
    let emptyMessage = 'You have no unread notification';

    function checkNotifications() {
        $.ajax({
            url: '/notifications/latest-notifications/',
            cache: false,
            success: function (data) {
                if (!data.includes(emptyMessage)) {
                    $("#notifications").addClass("text-danger");
                }
            },
        });
    };

    function update_social_activity (id_value) {
        let newsToUpdate = $("[news-id=" + id_value + "]");
        payload = {
            'id_value': id_value,
        };
        $.ajax({
            url: '/news/update-interactions/',
            data: payload,
            type: 'POST',
            cache: false,
            success: function (data) {
                $(".like-count", newsToUpdate).text(data.likes);
                $(".comment-count", newsToUpdate).text(data.comments);
            },
        });
    };

    checkNotifications();

    $('#notifications').popover({
        html: true,
        trigger: 'manual',
        container: "body" ,
        placement: "bottom",
    });

    $("#notifications").click(function (e) {
        if ($(".popover").is(":visible")) {
            $("#notifications").popover('hide');
            checkNotifications();
        }
        else {
            $("#notifications").popover('dispose');
            $.ajax({
                url: '/notifications/latest-notifications/',
                cache: false,
                success: function (data) {
                    $("#notifications").popover({
                        html: true,
                        trigger: 'focus',
                        container: "body" ,
                        placement: "bottom",
                        content: data,
                    });
                    $("#notifications").popover('show');
                    $("#notifications").removeClass("btn-danger")
                },
            });
        }
        return false;
    });

    let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    let ws_path = ws_scheme + '://' + window.location.host + "/ws/notifications/";
    let webSocket = new channels.WebSocketBridge();
    webSocket.connect(ws_path);

    // Helpful debugging
    webSocket.socket.onopen = function () {};

    webSocket.socket.onclose = function () {
        console.error("Disconnected from " + ws_path);
    };

    let caller = null;
    let calle = null;
    function goToVideoCall(){
        if(!document.hidden){
            let payload = {
                type: 'accept_call',
                caller: caller,
                calle: currentUser,
            };
            webSocket.send(payload);
            window.location.href = `/messages/video-call/${caller}/${calle}/`;
        }
    }

    function rejectCall(){
        if(!document.hidden){
            let payload = {
                type: 'reject_call',
                caller: caller,
                calle: calle,
            };
            webSocket.send(payload);
        }
    }

    $('body').on('click', '.answer-call-btn', goToVideoCall);
    $('body').on('click', '.reject-call-btn', rejectCall);

    let sender;
    function goToMessage(){
        if(!document.hidden){
            window.location.href = `/messages/${sender}/`;
        }
    }

    let questionUrl;
    function goToQuestion(){
        if(!document.hidden){
            window.location.href = questionUrl;
        }
    }

    function goToNews(){
        if(!document.hidden){
            window.location.href = '/news/';
        }
    }

    function showNotification(messageText){
        if(!Notify.needsPermission && window.visibilityState == 'hidden'){
            let notification = new Notify('sublime', {body : messageText});
            notification.show();
        }
    }

    let toasterOptions = {
        "closeButton": true,
        "debug": false,
        "newestOnTop": true,
        "progressBar": false,
        "positionClass": "toast-bottom-left",
        "preventDuplicates": false,
        "showDuration": "300",
        "hideDuration": "10",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    }

    let videoIcon = $($.parseHTML('<i class="fa fa-video-camera" aria-hidden="true"></i>'));
    let waitngResponse = false;

    // Listen the WebSocket bridge created throug django-channels library.
    webSocket.listen(function(event) {
        toastr.options = toasterOptions;
        switch (event.key) {
            case "notification":
                $("#notifications").addClass("btn-danger");
                break;

            case "social_update":
                console.log('--- social_update');
                $("#notifications").addClass("btn-danger");
                break;

            case "additional_news":
                console.log('--- additional_news');
                $(".stream-update").show();
                // if (event.actor_name !== currentUser) {
                // }
                break;

            case 'reply_news_post':
                $("#notifications").addClass("btn-danger");
                toasterOptions['onclick'] = goToNews;
                toastr["success"]("Reply", event.message_text);
                update_social_activity(event.id_value);
                break;

            case 'like_news_post':
                $("#notifications").addClass("btn-danger");
                toasterOptions['onclick'] = goToNews;
                toastr["success"]("Like", event.message_text);
                update_social_activity(event.id_value);
                break;

            case 'Vote':
                questionUrl = event.question_url;
                toasterOptions['onclick'] = goToQuestion;
                toastr["success"]("Vote", event.message_text);
                showNotification(event.message_text);
                break;

            case 'Answer':
                questionUrl = event.question_url;
                toasterOptions['onclick'] = goToQuestion;
                toastr["success"]("Answer", event.message_text);
                showNotification(`${event.actor_name} posted an answer on your question`);
                break;

            case 'Message':
                let doNotShowUrls = [
                    `/messages/${event.actor_name}/`,
                    `/messages/video-call/${event.actor_name}/${event.recipient}/`,
                    `/messages/video-call/${event.recipient}/${event.actor_name}/`,
                ];
                if(!doNotShowUrls.includes(window.location.pathname)){
                    sender = event.actor_name;
                    toasterOptions['onclick'] = goToMessage;
                    toastr["info"]("Message", event.message_text);
                    showNotification(`You received a new message from ${sender}`);
                }
                break;

            case 'VideoCall':
                calle = event.recipient;
                caller = event.actor_name;
                toasterOptions['timeOut'] = '10000';
                let notifBody = `${event.message_text}
                                <div class="call-notif-body">
                                    <button type="button" id="okBtn" class="btn btn-danger reject-call-btn">Reject</button>
                                    <button type="button" class="btn btn-success answer-call-btn" style="margin: 0 8px 0 8px">Accept</button>
                                </div>`;
                toastr['info'](notifBody);
                showNotification(event.message_text);
                break;

            case 'AcceptCall':
                caller = event.caller;
                calle = event.calle;
                waitngResponse = false;
                if(document.visibilityState == 'visible'){
                    window.location.href = `/messages/video-call/${event.caller}/${event.calle}/`;
                }
                break;

            case 'RejectCall':
                btnStopLoading($('.start-video-call button'), '', videoIcon);
                showCallRejected(event.calle);
                waitngResponse = false;
                break;

            default:
                console.log('error: ', event);
                break;
        };
    });

    function btnLoading(btn, loadingText, loadingIcon){
        btn.addClass('disabled');
        btn.text(loadingText);
        btn.append(loadingIcon);
    }

    function btnStopLoading(btn, text, icon){
        btn.empty();
        btn.text(text);
        btn.append(icon);
        btn.removeClass('disabled');
    }

    function showCallRejected(calle) {
        if(waitngResponse){
            toastr["warning"]("Video Call", `${calle} rejected your call.`);
            btnStopLoading($('.start-video-call button'), '', videoIcon);
        }
    }

    function showNoAnswer(calle){
        if(waitngResponse){
            toastr["warning"]("Video Call", `No answer from ${calle}.`);
            btnStopLoading($('.start-video-call button'), '', videoIcon);
        }
    }

    $('.start-video-call').on('submit', function(e){
        e.preventDefault();

        let $this = $(this);
        let submitBtn = $this.find('.btn.btn-success');
        let loadingIcon = $($.parseHTML('<i class="fa fa-circle-o-notch fa-spin" aria-hidden="true"></i>'));
        btnLoading(submitBtn, 'Calling... ', loadingIcon);
        let data = $this.serializeArray();
        let url = $this.attr('action');
        waitngResponse = true;

        $.ajax({
            url: url,
            data: data,
            method: 'POST',
            success: function(res){
                setTimeout(() => {
                    showNoAnswer(data[1].value);
                    waitngResponse = false;
                }, 10000);
            },
            error: function(error){
                console.log('invite error ', error);
            }
        });
    });
});
