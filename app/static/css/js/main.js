document.addEventListener("DOMContentLoaded", function () {

```
console.log("HotelStay JavaScript loaded successfully");


//  DATE VALIDATION
 
const checkIn =
    document.getElementById("check_in");

const checkOut =
    document.getElementById("check_out");


if (checkIn && checkOut) {

    // Today's date

    const today =
        new Date().toISOString().split("T")[0];


    checkIn.min = today;


    checkIn.addEventListener(
        "change",
        function () {

            checkOut.min = checkIn.value;


            if (
                checkOut.value &&
                checkOut.value <= checkIn.value
            ) {

                checkOut.value = "";

            }

        }
    );


    checkOut.addEventListener(
        "change",
        function () {

            if (
                checkIn.value &&
                checkOut.value <= checkIn.value
            ) {

                alert(
                    "Check-out date must be after check-in date."
                );

                checkOut.value = "";

            }

        }
    );

}


  
const deleteForms =
    document.querySelectorAll(
        ".delete-form"
    );


deleteForms.forEach(
    function (form) {

        form.addEventListener(
            "submit",
            function (event) {

                const confirmed =
                    confirm(
                        "Are you sure you want to delete this?"
                    );


                if (!confirmed) {

                    event.preventDefault();

                }

            }
        );

    }
);


 
const flashMessages =
    document.querySelectorAll(".flash");


flashMessages.forEach(
    function (message) {

        setTimeout(
            function () {

                message.style.opacity = "0";

                message.style.transition =
                    "opacity 0.5s";


                setTimeout(
                    function () {

                        message.remove();

                    },
                    500
                );

            },
            5000
        );

    }
);
```

});
