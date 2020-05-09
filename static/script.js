$(document).ready(function(){
    userData = {}
    bookingRequest = {}
    locationNames = {
        '161' : 'Midtown Center',
        '162' : 'Midtown East',
        '163' : 'Midtown North',
        '164' : 'Midtown South'
    }

    $('.screen').addClass('screenHidden');
    $('.bottomButton').addClass('bottomButtonHidden');
    $('.box').addClass('boxHiddenBottom');
    $('.box.login').removeClass('boxHiddenBottom');

    showError = function(err){
        console.log('Error: ' + err);
        $('.error').html('Error: ' + err);
        $('.error').addClass('errorShow');
        setTimeout(function(){
            $('.error').removeClass('errorShow');
        }, 6000);
    }

    showNotification = function(note){
        console.log('Notification: ' + note);
        $('.notification').html(note);
        $('.notification').addClass('notificationShow');
        setTimeout(function(){
            $('.notification').removeClass('notificationShow');
        }, 3500);
    }

    updateHomeScreen = function(){
        $('.screen.homeScreen').html('');
        if('history' in userData){
            if(!('bookings' in userData['history'])){
                userData['history']['bookings'] = [];
            }
            acceptsHTML = '<div class = "screenHeader">ACCEPTED BOOKINGS</div>';
            rejectsHTML = '<div class = "screenHeader">REJECTED BOOKINGS</div>';
            var i;
            for(i = 0 ; i < userData['history']['bookings'].length; i++){
                booking = userData['history']['bookings'][i]
                loc = booking['location'];
                if(loc in locationNames){
                    loc = locationNames[loc];
                }
                temp = '';
                temp += '<div id ="booking'+i.toString()+'" class = "booking">';
                temp += '<div class = "bookingData bookingDate">'+booking['Date'].toString()+'</div>';
                temp += '<div class = "bookingData bookingLocation">'+loc.toString()+'</div>';
                temp += '<div class = "bookingData bookingGroupSize">'+booking['Group Size'].toString()+'</div>';
                temp += '<div class = "bookingData bookingEntryTime">'+booking['Entry Time'].toString()+'</div>'; 
                temp += '<div class = "bookingData bookingExitTime">'+booking['Exit Time'].toString()+'</div>';
                temp += '</div>';
                if(booking['Decision']){
                    acceptsHTML += temp;
                }
                else{
                    rejectsHTML += temp;
                }
            }
        }
        $('.screen.homeScreen').html(acceptsHTML + rejectsHTML);
    }

    $('.login .submitButton').click(function(){
        console.log('Trying to login')
        data = {'number': $('.login .number').val(), 'password':$('.login .password').val()}
        $.post("/login", data, function(response){
            console.log('RESPONSE: ');
            res = JSON.parse(response);
            console.log(res);
            if(res['error'] == 'False'){
                userData = res['data'];
                $('.login,.register').addClass('boxHiddenBottom');
                showNotification('Welcome back '+ res['data']['name']);
                updateHomeScreen();
                $('.homeScreen').removeClass('screenHidden');
                $('.newBooking').removeClass('bottomButtonHidden');
            }
            else{
                showError(res['error']);
            }
        });
    });

    $('.register .submitButton').click(function(){
        console.log('Trying to Register')
        data = {'name': $('.register .name').val() , 'number': $('.register .number').val(), 'password':$('.register .password').val()}
        $.post("/register", data, function(response){
            console.log('RESPONSE: ')
            res = JSON.parse(response)
            console.log(res)
            if(res['error'] == 'False'){
                userData = res['data']
                $('.login,.register').addClass('boxHiddenBottom');
                showNotification('Hello ' + res['data']['name']);
                updateHomeScreen();
                $('.homeScreen').removeClass('screenHidden');
                $('.newBooking').removeClass('bottomButtonHidden');
            }
            else{
                showError(res['error']);
            }
        });
    });

    $('.gotoRegister').click(function(){
        $('.box.login').addClass('boxHiddenBottom');
        $('.box.register').removeClass('boxHiddenBottom');
    });

    $('.gotoLogin').click(function(){
        $('.box.register').addClass('boxHiddenBottom');
        $('.box.login').removeClass('boxHiddenBottom');
    });

    $('.newBooking').click(function(){
        $('.screen').addClass('screenHidden');
        $('.bottomButton').addClass('bottomButtonHidden');
        $('.locationsScreen').removeClass('screenHidden');
        $('.selectDestination').removeClass('bottomButtonHidden');
        $('.locationsScreen *').removeClass('mapElementHidden');
    });
    
    $('.map').click(function(event){
        $('.zoneCursor').removeClass('cursorHidden');
        $('.locationsScreen .zoneCursor').css({
            "left" : event.clientX,
            "top" : event.clientY
        });
        $('.locationsScreen .zoneCursor .label').html('No service in this area');
        bookingRequest['location'] = undefined;
    });

    $('.locationsScreen .zone').click(function(event){
        $('.zoneCursor').removeClass('cursorHidden');
        zoneID = $(this).html().toString();
        zoneName = locationNames[zoneID];
        $('.locationsScreen .zoneCursor').css({
            "left" : event.clientX,
            "top" : event.clientY
        });
        $('.locationsScreen .zoneCursor .label').html(zoneName);
        bookingRequest['location'] = zoneID;
    });

    $('.bottomButton.selectDestination').click(function(){
        if('location' in bookingRequest){
            if(bookingRequest['location'] != undefined){
                $('.screen').addClass('screenHidden');
                $('.bottomButton').addClass('bottomButtonHidden');
                $('.locationsScreen *').addClass('mapElementHidden');
                $('.timeScreen').removeClass('screenHidden');
                $('.requestBooking').removeClass('bottomButtonHidden');
                console.log('location Selected !');
                console.log(bookingRequest);
            }
            else{
                showError('Service not available for selected location.');
            }
        }
        else{
            showError('Please select a location');
        }
    });

    $('input.date').change(function(){
        param = 'Date'
        value = $(this).val();
        console.log(param + ' Updated: '+ value.toString());
        bookingRequest[param] = value;
    });
    $('input.entryTime').change(function(){
        param = 'Entry Time'
        value = $(this).val();
        console.log(param + ' Updated: '+ value.toString());
        bookingRequest[param] = value;
    });
    $('input.exitTime').change(function(){
        param = 'Exit Time'
        value = $(this).val();
        console.log(param + ' Updated: '+ value.toString());
        bookingRequest[param] = value;
    });
    $('input.groupSize').change(function(){
        param = 'Group Size'
        value = $(this).val();
        console.log(param + ' Updated: '+ value.toString());
        bookingRequest[param] = value;
    });

    $('.requestBooking').click(function(){
        if(!('Date' in bookingRequest)){
            console.log('Date not found');
            showError('Please enter a date');
            return
        }
        else if(!('Entry Time' in bookingRequest)){
            console.log('Entry Time not found');
            showError('Please enter an entry Time');
            return
        }
        else if(!('Exit Time' in bookingRequest)){
            console.log('Exit Time not found');
            showError('Please enter an exit time');
            return
        }
        else if(!('Group Size' in bookingRequest)){
            console.log('Group Size not found');
            showError('Please enter the group size');
            return
        }
        else{
            console.log('REQUESTING BOOKING: ');
            console.log(bookingRequest);
            bookingRequest['number'] = userData['number']
            data = bookingRequest
            $.post("/booking", data, function(response){
                console.log('RESPONSE: ');
                res = JSON.parse(response);
                console.log(res);
                if(res['error'] == 'False'){
                    showNotification('Booking Successful');
                    userData = res['data']
                    $('.screen').addClass('screenHidden');
                    $('.bottomButton').addClass('bottomButtonHidden');
                    updateHomeScreen();
                    $('.homeScreen').removeClass('screenHidden');
                    $('.newBooking').removeClass('bottomButtonHidden');
                }
                else{
                    if('data' in res){
                        userData = res['data']
                        console.log(userData)
                    }
                    showError(res['error']);
                    $('.screen').addClass('screenHidden');
                    $('.bottomButton').addClass('bottomButtonHidden');
                    updateHomeScreen();
                    $('.homeScreen').removeClass('screenHidden');
                    $('.newBooking').removeClass('bottomButtonHidden');
                }
            });
        }
    });

    $('body').on('click', '.homeScreen .booking', function() {
        id = parseInt($(this).attr('id').substr(7));
        booking = userData['history']['bookings'][id];
        if(booking['Decision'] && 'QRCode' in booking){
            QRCodeStr = '[APPROVED] | CONF CODE: ' + booking['QRCode'] + ' | ';
            QRCodeStr += 'GROUP: ' + booking['Group Size'] + ' | ';
            QRCodeStr += 'LOC: ' + booking['location'] + ' | '
            QRCodeStr += 'TIME: ' + booking['Entry Time'] + ' - ' + booking['Exit Time'];
            console.log('QR CODE STRING: ' + QRCodeStr);
    
            $('#qrcode').ClassyQR({
                type:'text',
                text: QRCodeStr
            });
    
            $('.QRCode').addClass('QRCodeShow');
            $('.QRClose').addClass('QRCloseShow');
            $('.QRCurtain').addClass('QRCurtainShow');
        }
        else{
            showNotification('This is a rejected booking');
        }
    });

    $('.QRClose').click(function(){
        $('.QRCode').removeClass('QRCodeShow');
        $('.QRClose').removeClass('QRCloseShow');
        $('.QRCurtain').removeClass('QRCurtainShow');
    });
});