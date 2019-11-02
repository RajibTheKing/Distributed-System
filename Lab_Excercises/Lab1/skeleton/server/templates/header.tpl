<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">

    <title>Distributed blackboard</title>

    <!-- Custom fonts for this template-->
    <link href="templates/vendor/fontawesome-free/css/all.min.css" rel="stylesheet" type="text/css">
    <link
    href="https://fonts.googleapis.com/css?family=Nunito:200,200i,300,300i,400,400i,600,600i,700,700i,800,800i,900,900i"
    rel="stylesheet">

    <!-- Custom styles for this template-->
    <link href="templates/css/sb-admin-2.min.css" rel="stylesheet">

</head>

<body id="page-top">

    <!-- Page Wrapper -->
    <div id="wrapper">

        <!-- Content Wrapper -->
        <div id="content-wrapper" class="d-flex flex-column">

            <!-- Main Content -->
            <div id="content">

                <!-- Begin Page Content -->
                <div class="container-fluid">

                    <!-- Page Heading -->
                    <div class="d-sm-flex align-items-center justify-content-between mb-4">
                        <h1 class="h3 mt-4 mb-0 text-gray-800">Distributed blackboard - {{board_title}}</h1>
                    </div>

                    <!-- Content Row -->
                    <div class="row">
                        <!-- Client input space-->
                        <div class="card shadow mb-4 w-100">
                            <div class="card-header py-3">
                                <h6 class="font-weight-bold text-primary">Client Input</h6>
                            </div>
                            <div class="card-body">
                                <h3>Submit a message to the board</h3>
                                <form id="usrform" action="/board" target="noreload" method="post">
                                    <input type="text" name="entry" size="100%" autofocus required />
                                    <span class="text mt-4 mb-0 float-right"><input type="submit" value="Submit to board"/></span>
                                </form>
                            </div>
                        </div>
                    </div>