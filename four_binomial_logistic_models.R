library(boot)

plant_data = read.csv("4_binomials_plant_data.csv")
plant_data = plant_data[plant_data$Fuel!="Other ",] #removed "Other" fuel types, was causing errors in our model
plant_data = plant_data[plant_data$Cooling.Type.1.=="Mechanical Draft" |plant_data$Cooling.Type.1.=="Natural Draft" | plant_data$Cooling.Type.1.=="Once-Through" |plant_data$Cooling.Type.1.=="Dry", ]
state_df = model.matrix(~plant_data$State)
rownames(plant_data) <- 1:nrow(plant_data)
plant_data = merge(plant_data, state_df, by=0, all=TRUE)
plant_data$STYPE[plant_data$STYPE=="#N/A"] = "N/A"
plant_data = droplevels(plant_data)

shuffled_data =  plant_data[sample(nrow(plant_data)),] #shuffle data

#split data into training and test sets
test_data = shuffled_data[1:80,]
training_data = shuffled_data[81:nrow(shuffled_data),]


#define cost function for accuracy

cost <- function(labels,pred){
  mean(labels==ifelse(pred > 0.5, 1, 0))
}

#function that averages the results of n separate knn cross validations
#input your data, your model, and the number of times you want to cross validate and average over
xvalidate <- function(data, model, n){
  x_val_df = as.data.frame(matrix(,nrow=n,ncol=2))
  for (i in 1:n){
    x_val=cv.glm(data, model, cost, K=10)
    x_val_df[i,] = x_val$delta
  }
  x_val_delta = colSums(x_val_df)/nrow(x_val_df)
  return (x_val_delta)
}

#train glm models 
#use k-folds cross-validation to get accuracy (model selection)


#training and validating different mechanical draft models
mechanical_draft_data = training_data[,c(4,5,9,25,39)]
fit_mechanical_draft_1 <- glm(mechanical_draft~ .,data=mechanical_draft_data,family=binomial())
xvalidate(mechanical_draft_data, fit_mechanical_draft_1, 30) #63%

mechanical_draft_data = training_data[,c(4,5,9,25,27,39)]
fit_mechanical_draft_2 <- glm(mechanical_draft~ .,data=mechanical_draft_data,family=binomial())
xvalidate(mechanical_draft_data, fit_mechanical_draft_2, 30) #65%

mechanical_draft_data = training_data[,c(4,5,6,9,25,27,39)]
fit_mechanical_draft_3 <- glm(mechanical_draft~ .,data=mechanical_draft_data,family=binomial())
xvalidate(mechanical_draft_data, fit_mechanical_draft_3, 30) #64%

mechanical_draft_data = training_data[,c(4,5,9,25,39,41:70)] #added states, decreases accuracy
fit_mechanical_draft_4 <- glm(mechanical_draft~ .,data=mechanical_draft_data,family=binomial())
xvalidate(mechanical_draft_data, fit_mechanical_draft_4, 30) #61%

mechanical_draft_data = training_data[,c(4,5,25,39)]
fit_mechanical_draft_5 <- glm(mechanical_draft~ .,data=mechanical_draft_data,family=binomial())
xvalidate(mechanical_draft_data, fit_mechanical_draft_5, 30) #60%

mechanical_draft_data = training_data[,c(4,25,39)] 
fit_mechanical_draft_6 <- glm(mechanical_draft~ .,data=mechanical_draft_data,family=binomial())
xvalidate(mechanical_draft_data, fit_mechanical_draft_6, 30) #60%

#natural draft 

natural_draft_data = training_data[,c(4,5,6,9,25,27,38)]
fit_natural_draft_1 <- glm(natural_draft~ .,data=natural_draft_data,family=binomial())
xvalidate(natural_draft_data, fit_natural_draft_1, 30) #82%, pretty good

natural_draft_data = training_data[,c(4,25,27,38)]
fit_natural_draft_2 <- glm(natural_draft~ .,data=natural_draft_data,family=binomial())
xvalidate(natural_draft_data, fit_natural_draft_2, 30) #82%, other variables didn't contribute much

#dry 
dry_data = training_data[,c(4,25,27,40)]
fit_dry_1 <- glm(dry~ .,dry_data,family=binomial())
xvalidate(dry_data, fit_dry_1, 30) #86%, pretty simple model

dry_data_2 = training_data[,c(4,5,6,9,25,27,40)]
fit_dry_2 <- glm(dry~ .,dry_data,family=binomial())
xvalidate(dry_data, fit_dry_2, 30) #86%, did a little worse than the simpler model

#training and validating once through models

once_through_data = training_data[,c(4,5,9,25,37)]
fit_once_through_1 <- glm(once_through~ .,data=once_through_data,family=binomial())
xvalidate(once_through_data, fit_once_through_1, 30) #94% accuracy

once_through_data = training_data[,c(4,37)]
fit_once_through_2 <- glm(once_through~ .,data=once_through_data,family=binomial())
xvalidate(once_through_data, fit_once_through_2, 30) #92% accuracy


#winning models: fit_mechanical_draft_2, fit_natural_draft_2, fit_dry_1, fit_once_through_1

#write accuracy function that inputs predicted labels and labels, outputs accuracy
accuracy <- function(y, y_pred){
  
}

#test accuracies
test_mechanical_draft = test_data[,c(4,5,9,25,27,39)]
predicted_test_mechanical_draft = predict(fit_mechanical_draft_2, test_mechanical_draft, type="response") #predicted probabilities
cost(test_data$mechanical_draft,as.vector(unlist(predicted_test_mechanical_draft)))
#test accuracy: 71.25%

test_natural_draft = test_data[,c(4,25,27,38)]
predicted_test_natural_draft = predict(fit_natural_draft_2, test_natural_draft, type="response")
cost(test_data$natural_draft,as.vector(unlist(predicted_test_natural_draft)))
#test accuracy: 78.75%

test_dry = test_data[,c(4,25,27,40)]
predicted_test_dry = predict(fit_dry_1, test_dry, type="response")
cost(test_data$dry,as.vector(unlist(predicted_test_dry)))
#test accuracy: 88.75%

test_once_through = test_data[,c(4,5,9,25,37)]
predicted_test_once_through = predict(fit_once_through_1, test_once_through, type="response")
cost(test_data$natural_draft,as.vector(unlist(predicted_test_once_through)))
#test accuracy: 82.5%
