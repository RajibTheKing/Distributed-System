#Simple methods that the byzantine node calls to decide what to vote.


#Compute byzantine votes for round 1, by trying to create
#a split decision.
#input: 
#	number of loyal nodes,
#	number of total nodes,
#	Decision on a tie: True or False 
#output:
#	A list with votes to send to the loyal nodes
#	in the form [True,False,True,.....]
def compute_byzantine_vote_round1(no_loyal,no_total,on_tie):

  result_vote = []
  for i in range(0,no_loyal):
    if i%2==0:
      result_vote.append(not on_tie)
    else:
      result_vote.append(on_tie)
  return result_vote

#Compute byzantine votes for round 2, trying to swing the decision
#on different directions for different nodes.
#input: 
#	number of loyal nodes,
#	number of total nodes,
#	Decision on a tie: True or False
#output:
#	A list where every element is a the vector that the 
#	byzantine node will send to every one of the loyal ones
#	in the form [[True,...],[False,...],...]
def compute_byzantine_vote_round2(no_loyal,no_total,on_tie):
  
  result_vectors=[]
  for i in range(0,no_loyal):
    if i%2==0:
      result_vectors.append([on_tie]*no_total)
    else:
      result_vectors.append([not on_tie]*no_total)
  return result_vectors

