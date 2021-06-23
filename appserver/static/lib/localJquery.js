require.config({
   paths: {
       'local': '../app/nlp-text-analytics/lib/jquery-3.6.0.min'
   },
   shim: {
       local: {
           exports: '$'
       }
   }
});

define(
  
   ['local'],
 
   function($) {
       return $.noConflict(true);
   }
 
);
