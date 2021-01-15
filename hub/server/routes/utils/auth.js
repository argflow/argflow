function checkAuthenticated(context) {
    return context.isAuthenticated();
}

function checkAdmin(context) {
    return new Promise((resolve, reject) => {
        if (context.isAuthenticated()) {
            queries.getSingleUser(context.state.user.id)
                .then((user) => {
                    if (user && user[0].admin == 1) resolve(true);
                    resolve(false);
                })
                .catch((err) => { reject(false); });
        }
        return false;
    });
}

module.exports = {
    checkAuthenticated,
    checkAdmin
}