
//Audio recording functionality
var errorCallback = function(e)
{
    console.log("not working")
}

function convertFloat32ToInt16(buffer) {
    l = buffer.length;
    buf = new Int16Array(l);
    while (l--) {
      buf[l] = Math.min(1, buffer[l])*0x7FFF;
    }
    return buf.buffer;
  }

function recorderProcess(e) {
    var left = e.inputBuffer.getChannelData(0);    
}

var recorder;
var audio = document.querySelector('audio');

function startRecording(){
  navigator.getUserMedia  = navigator.getUserMedia ||
                            navigator.webkitGetUserMedia ||
                            navigator.mozGetUserMedia ||
                            navigator.msGetUserMedia;

  if (navigator.getUserMedia) {
    navigator.getUserMedia({audio: true, video: false}, function(s) {
      var context = new AudioContext();
      var mediaStreamSource = context.createMediaStreamSource(s);
      recorder = new Recorder(mediaStreamSource);
      recorder.record();
    }, errorCallback);
  } else {
      console.log('media stream not found')
  }
}    

function stopRecording() {
  recorder.stop();

  // Conversion of audio recording to WAV file and file upload
  recorder.exportWAV(function(blob) {
     var url = window.URL.createObjectURL(blob);
     var language = $('#languageDropdown').val()
     var data = new FormData();
     data.append('file', blob);
     data.append('language', language);


    // Ajax request to backend upon recording completion
    $.ajax({
      url: '/speechToText',
      type: 'POST',
      data: data,
      processData: false,
      contentType: false,
      success: function(response) {
        parsed = JSON.parse(response)
        $('#count').text(parsed['count'])
        //Create chart of tone analysis results
        var ctx = $('#chart')
        var myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ["Anger", "Disgust", "Fear", "Joy", "Sadness"],
                datasets: [{
                    data: [parseFloat(parsed['anger']),
                           parseFloat(parsed['disgust']),
                           parseFloat(parsed['fear']),
                           parseFloat(parsed['joy']),
                           parseFloat(parsed['sadness']),],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255,99,132,1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero:true
                        }
                    }]
                }
            }
        });
        myChart.options.legend.display = false; 
        //Provide original and translated text on user interface
        $('#translatedText').text(parsed['translatedText'])
        $('#originalText').text(parsed['originalText'])
      

      },
      error: function() {
        alert("Your feedback was not processed correctly, please try again.")
      }
  });
});
}

  
