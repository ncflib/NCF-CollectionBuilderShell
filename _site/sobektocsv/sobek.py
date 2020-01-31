<html>
<head>
    <script
  src="https://code.jquery.com/jquery-3.4.1.min.js"
  integrity="sha256-CSXorXvZcTkaix6Yvo6HppcZGetbYMGWSFlBw8HfCJo="
  crossorigin="anonymous"></script>
    <script>
    
    function start() {
        var link = $("#sobekApi").val();

        $.get( link, function( data ) {
            alert( "Data Loaded: " + data );
        });

        $.ajax({
            url: link,
            context: ""
            }).done(function(data) {
            alert(data);
            });
    }
    
    </script>
</head>
<body>

    <input type="text" id="sobekApi" placeholder="Please insert the link from OAI 2.0" />
    <button onClick="start()">Send</button>

</body>
</html>