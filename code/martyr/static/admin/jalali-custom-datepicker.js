$(function () {
  function activateDatepicker() {
    $(".vjDateField").each(function () {
      var inputId = $(this).attr("id") || "";
      if (inputId.includes("__prefix__")) {
        return;
      }

      $(this).datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        showOn: "both",
        buttonImageOnly: true,
        isRTL: false,
        buttonText: "یک تاریخ انتخاب کنید",
        yearRange: "1280:1450",
      });
    });
  }

  if (!$.datepicker) {
    $ = django.jQuery;
  }
  activateDatepicker();

  $(document).on("formset:added", function (event, $row, formsetName) {
    activateDatepicker();
  });

  $(document).on("formset:removed", function (event, $row, formsetName) {
    activateDatepicker();
  });
});
