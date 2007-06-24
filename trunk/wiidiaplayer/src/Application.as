
      class Application extends MovieClip {
        static function main() {
          _root.createTextField("info", 0, 0, 5, Stage.width, 20);
          _root.info.setNewTextFormat(new TextFormat("Arial", 10));
          _root.info.text = "Webcam: Click the image to capture";
          return
       
          var display = _root.attachMovie("VideoDisplay", "display", _root.getNextHighestDepth());
          var cam = Camera.get();
          display.video._y = 30;
          display.video._width = 320;
          display.video._height = 240;
          display.video.attachVideo(cam);
       
          display.onPress = function() {
            var bd = new BitmapData(320, 240);
            var pixels = new Array();
            var w = bd.width;
            var h = bd.height;
            var out = new LoadVars();
       
            bd.draw(display.video, new Matrix());
            for (var a = 0; a <w; a++) {
              for (var b = 0; b <h; b++) {
                var tmp = bd.getPixel(a, b).toString(32);
                pixels.push(tmp);
              }
            }
            out.img = pixels.join(",");
            out.height = h;
            out.width = w;
            out.send("image_upload", "image_upload_frame", "POST");
          }
        }
      }
