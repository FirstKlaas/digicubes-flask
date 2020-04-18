DigiCubes = {}

DigiCubes.token = null;
DigiCubes.routes = {}

DigiCubes.addRoute = function(name, path) {
    DigiCubes.routes[name] = path
}

/**
 * Login to the digicube server. If successfull, it will return
 * a bearer token for authorization.
 * 
 * @param {string} login 
 * @param {string} password 
 */
DigiCubes.login = async function(login = 'root', password = 'digicubes') {
    data = {
        login: login,
        password: password
    }
    const response = await fetch('/account/login/', {
        method: 'GET',
        mode: 'same-origin',
        cache: 'default',
        credentials: 'include',
        headers: {},
        redirect: 'follow',
        referrer: 'no-referrer',
    });
    if (response.status == 200) {
        const json = await response.json();
        DigiCubes.token = json.bearer_token;
        return json.bearer_token;
    }

    if (response.status == 404) {
        throw new Error("Authorization failed")
    }

    throw new Error("Server error");
}

DigiCubes.getUsers = async function(token) {
    const response = await fetch('/account/users/', {
        method: 'GET',
        mode: 'same-origin',
        cache: 'default',
        credentials: 'include',
        headers: {
            'Authorization': 'Bearer ' + token,
        },
        redirect: 'follow',
        referrer: 'no-referrer'
    });
    if (response.status == 200) {
        return response.text();
    } else {
        throw new Error(response.text);
    }
}

DigiCubes.getUserTable = async function(offset = null, count = null) {
    path = DigiCubes.routes["account.panel-user-table"]
    url = new URL(path, window.location)
    if (offset != null) {
        url.searchParams.append('offset', offset)
    }
    if (count != null) {
        url.searchParams.append('count', count)
    }

    result = await fetch(url, {
            method: 'GET',
            mode: 'same-origin',
            cache: 'default',
            credentials: 'include',
            redirect: 'follow',
            referrer: 'no-referrer'
        })
        .then(response => {
            if (response.status == 200) {
                return response.text();
            }
            throw new Error(response.statusText);
        })
        .catch(error => {
            console.log(error);
            return "";
        });

    return result;
}

DigiCubes.addUserRole = async function(user_id, role_id) {

    data = {
        "user_id" : user_id,
        "role_id" : role_id
    };

    DigiCubes.rfc("PUT", "ADD_USER_ROLE", data).then((response) => {
        return response.json();
    })
    .then((data) => {
        console.log(data);
    });
}

DigiCubes.toggleUserActiveState = async function(user_id) {
    data = {
        "user_id" : user_id
    };

    return DigiCubes.adminRFC("PUT", "USER_SET_ACTIVE_STATE", data)
    .then((response_data) => {
        return response_data.data;
    });
}

DigiCubes.toggleUserVerifiedState = async function(user_id) {
    data = {
        "user_id" : user_id
    };

    return DigiCubes.adminRFC("PUT", "USER_SET_VERIFIED_STATE", data)
    .then((response) => {
        return response.data;
    });
}

DigiCubes.getSchoolCoursesInfo = async function(school_id) {
    data = {
        "school_id" : school_id 
    }
    return DigiCubes.adminRFC(
        "PUT", "SCHOOL_GET_COURSE_INFO", data)
    .then((response_data) => {
        return response_data.data
    });
}

DigiCubes.toggleUserRole = async function(user_id, role_id, operation = "toggle") {
    return DigiCubes.adminRFC(
        "PUT", "USER_TOGGLE_ROLE",
        {
            "user_id" : user_id,
            "role_id" : role_id,
            "operation" : operation
        })
    .then((response_data) => {
        return response_data.data
    });
}

DigiCubes.adminRFC = async function(method, funcName, data) {
    return fetch('/dcad/rfc/', {
        method: method,
        mode: 'same-origin',
        cache: 'default',
        credentials: 'same-origin',
        redirect: 'follow',
        referrer: 'no-referrer',
        headers: {
            'x-digicubes-rfcname': funcName,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then((response) => {
        if (response.ok) {
            return response.json();
        };
        throw Error(response.statusText)
    })
}
