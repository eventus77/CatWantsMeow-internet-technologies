function numberCheck(func) {
    return function(param) {
        if (typeof(param) != "number") {
            throw Error(param + " is not a number");
        }
        return func(param);
    }
}

function typeCheck(func, type) {
    return function() {
        for (var i = 0; i < arguments.length; i++) {
            if (typeof(arguments[i]) != type) {
                throw Error("Parameter " + arguments[i] + " is not " + type);
            }
        }
        return func.apply(null, arguments);
    }
}


function avg() {
    var sum = 0;
    for (var i = 0; i < arguments.length; i++) {
        sum += arguments[i];
    }
    return sum / arguments.length;
}


alert(typeCheck(avg, "number")(12, 43))
