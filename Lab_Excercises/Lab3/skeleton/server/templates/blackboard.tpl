                    <div id="boardcontents_placeholder">
                    <div class="row">
                    <!-- this place will show the actual contents of the blackboard. 
                    It will be reloaded automatically from the server -->
                        <div class="card shadow mb-4 w-100">
                            <div class="card-header py-3">
                                <h6 class="font-weight-bold text-primary">Blackboard content</h6>
                            </div>
                            <div class="card-body">
                                <input type="text" name="id" value="ID" size="50%%" readonly>
                                <input type="text" name="entry" value="Entry" size="50%%" readonly>
                                % for board_entry, board_element in board_dict:
                                    <form class="entryform" target="_self" method="post" action="/board/{{board_entry}}/">
                                        <input type="text" name="id" value="{{board_entry}}" size="50%%" readonly disabled> <!-- disabled field won’t be sent -->
                                        <input type="text" name="entry" value="{{board_element}}" size="50%%">
                                        <button type="submit" name="delete" value="0">Modify</button>
                                        <button type="submit" name="delete" value="1">X</button>
                                    </form>
                                %end
                            </div>
                        </div>
                    </div>
                    </div>