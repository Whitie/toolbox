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
                    el.notify(gettext('Something went wrong'), 'warn');
                } else {
                    console.log('Saved');
                    el.notify(gettext('Saved'), 'success');
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
            window.location.reload();
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

function switch_tab() {
    $('.tb-tab').toggleClass('is-active');
    $('.columns').toggleClass('is-hidden');
}

function change_state(folder_id) {
    var url = $('#folder_'+folder_id).data('url');
    $.get(url).done(function() {
        window.location.reload();
    });
}

function save_molecules(molecules, image_data) {
    console.log('Saving molecules');
    var url = $('#molecules').data('url');
    var data = {image: image_data, molecules: molecules};
    $.alertable.prompt(gettext('Name')).then(function(formdata) {
        data['name'] = formdata.value;
        $.ajax({
            method: 'POST',
            url: url,
            data: JSON.stringify(data),
            processData: false,
            contentType: false,
            headers: {'X-CSRFToken': getCookie('csrftoken')}
        }).done(function(msg) {
            console.log(msg);
            $.notify(gettext('Molecules saved.'), 'success');
        });
    });
}

$(document).ready(function() {
    $('.navbar-burger').click(function() {
        $('.navbar-burger').toggleClass('is-active');
        $('.navbar-menu').toggleClass('is-active');
    });
    if ($('.card-header-title').length) {
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
    if ($('#btn-new-chem').length) {
        console.log('Molecules enabled');
    }
});
