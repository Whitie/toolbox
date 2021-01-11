// Custom functions for Toolbox

// From the Django docs (CSRF)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function save_inline_edit(event) {
    var esc = event.which == 27;
    var nl = event.which == 13;
    var el = event.target;
    var input = el.nodeName != 'INPUT' && el.nodeName != 'TEXTAREA';
    var data = {};
    if (input) {
        if (esc) {
            // restore state
            document.execCommand('undo');
            el.blur();
        } else if (nl) {
            // save
            el = $(el);
            var url = el.data('url');
            data['name'] = el.text().trim();
            data['id'] = el.data('id');
            $.ajax({
                method: 'POST',
                url: url,
                data: data,
                headers: {'X-CSRFToken': getCookie('csrftoken')}
            }).done(function(msg) {
                if (msg != 'ok') {
                    document.execCommand('undo');
                    $.notify(gettext('Error on save'), 'error');
                } else {
                    $.notify(gettext('Saved'), 'success');
                }
            });
            el.blur();
            event.preventDefault();
        }
    }
}

function add_folder() {
    $.alertable.prompt(gettext('Add new Folder'), {
        prompt: '<label>' + gettext('Name') + '</label>' +
                '<input type="text" class="alertable-input" name="name" maxlength="50">' +
                '<label>' +
                '<input type="checkbox" name="public"> ' +
                gettext('Public') +
                '</label>'
    }).then(function(data) {
        var url = $('#btn-add-folder').data('url');
        var to_send = {name: data.name};
        if (data.public) {
            to_send['public'] = data.public;
        }
        $.ajax({
            method: 'POST',
            url: url,
            data: to_send,
            headers: {'X-CSRFToken': getCookie('csrftoken')}
        }).done(function(msg) {
            console.log(msg);
            $.notify(gettext('Folder created: ') + data.name + '\n' +
                     gettext('Press reload to see it.'),
                     'success');
        });
    });
}

function save_whiteboard(image, done) {
    var url = $('#whiteboard').data('url');
    $.alertable.prompt(gettext('Name')).then(function(formdata) {
        var data = new FormData();
        data.append('content', image.asBlob(), image.suggestedFileName());
        data.append('name', formdata.value);
        $.ajax({
            method: 'POST',
            url: url,
            data: data,
            processData: false,
            contentType: false,
            headers: {'X-CSRFToken': getCookie('csrftoken')}
        }).done(function(msg) {
            console.log(msg);
            done(false);
            $.notify(gettext('Whiteboard saved.'), 'success');
        });
    });
}

$(document).ready(function() {
    if ($('.card-header').length) {
        console.log('Inline editing enabled');
        $(document).on('keydown', save_inline_edit);
    }
    if ($('#btn-add-folder').length) {
        console.log('Add folder enabled');
        $('#btn-add-folder').click(add_folder);
    }
    if ($('#btn-new-whiteboard').length) {
        console.log('Whiteboard enabled');
    }
});
