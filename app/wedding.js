function resizeMap() {
  var mapContainer = $('.map-featurette-container');
  var width = mapContainer.width();
  mapContainer.height(width + 'px');
}
$(resizeMap);
$(window).resize(resizeMap);
