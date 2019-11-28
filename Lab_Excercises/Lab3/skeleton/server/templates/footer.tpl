                    <div class="row">
                        <!-- Automatic board content reloader: shows if request was successful or failed -->
                        <div class="card shadow mb-4 w-100">
                            <div class="card-header py-3">
                                <h6 class="font-weight-bold text-primary">Automatic page reload</h6>
                            </div>
                            <div class="card-body">
                                <!-- this place will show a count down for the automatic reload of the board contents, downloaded periodically from the server using the javascript function reload_countdown. -->
                                <div id="countdown_placeholder"></div>
                                <!-- this place will show the actual contents of the blackboard. It will be reloaded automatically from the server -->
                                <!-- This place shows the status of the auto-reload. An error shown here means the server is not responding -->
                                <div id="boardcontents_status_placeholder">0: success</div>
                                <iframe name="noreload" style="display:none;"></iframe>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <!-- End Main Content -->
            <footer class="sticky-footer bg-white">
                <div class="container my-auto">
                    <div class="copyright text-center my-auto">
                        <span>Group members: {{members_name_string}}</span>
                    </div>
                </div>
            </footer>
            <!-- End of Footer -->

        </div>
        <!-- End of Content Wrapper -->

    </div>
    <!-- End of Page Wrapper -->

    <!-- Scroll to Top Button-->
    <a class="scroll-to-top rounded" href="#page-top">
        <i class="fas fa-angle-up"></i>
    </a>
    <!-- Bootstrap core JavaScript-->
    <script src="templates/vendor/jquery/jquery.min.js"></script>
    <script src="templates/vendor/bootstrap/js/bootstrap.bundle.min.js"></script>
    <!-- Core plugin JavaScript-->
    <script src="templates/vendor/jquery-easing/jquery.easing.min.js"></script>
    <!-- Custom scripts for all pages-->
    <script src="templates/js/sb-admin-2.min.js"></script>
    <!-- Page level plugins -->
    <script src="templates/vendor/chart.js/Chart.min.js"></script>
    <!-- Page level custom scripts -->
    <script src="templates/js/demo/chart-area-demo.js"></script>
    <script src="templates/js/demo/chart-pie-demo.js"></script>
    <!-- Inlined javascript code. This could be optionally hosted in another file on the server and included using 'src' attribute as above -->
    <script>
                var page_reload_timeout = 5; //in seconds
                var page_reload_count = 0;
                function update_contents(){
                    page_reload_count += 1;
                    $("#boardcontents_placeholder").load("/board #boardcontents_placeholder", function (data, status) {
                        //alert("Data: " + data + "\nStatus: " + status);
                        $("#boardcontents_status_placeholder").text(page_reload_count + ": " + status);
                    });
                }
                function reload_countdown(remaining) {
                    $("#countdown_placeholder").text("reloading page in: " + remaining + " seconds.");
                    if (remaining <= 0) {
                        remaining = page_reload_timeout;
                        update_contents();
                    }

                    setTimeout(function () {
                        reload_countdown(remaining - 1);
                    }, 1000);
                }
                $(document).ready(function () {
                    reload_countdown(page_reload_timeout);
                    $(".entryform").submit(update_contents);
                });
    </script>
</body>
</html>