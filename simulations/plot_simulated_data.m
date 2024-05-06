%% Define files
fns = {'sim_output_turing_test_500students.xlsx',... % 2 concepts
       'sim_output_rational_agents_500students.xlsx',... % 3 concepts
       'sim_output_history_of_ai_500students.xlsx',... % 3 concepts
       'sim_output_ai_intro_and_defs_500students.xlsx',... % 2 concepts
       'sim_output_search_500students.xlsx'}; % 5 concepts

parent_dir = './sim_data/';

%% Setup Constants and Variables
numStudents = 500;
endLen = 20;
netConcepts = 15;

M_difficulty_agnostic = zeros(numStudents,endLen);
M_difficulty_included = zeros(numStudents,endLen);
M_static = zeros(numStudents,endLen);

%% Iterate and Concatenate Data
netsum = 0;
for fn=fns
    ca = readcell([parent_dir,fn{1}]);
    
    header = ca(1,:);
    data = ca(2:end,:);
    
    
    for i=1:size(data,1)
        curStudent = data{i,1};
        
        %% Make vector of data 20 long regardless of how long the real data is
        curStudentData = [];
        for j=2:endLen+1
            if length(data(i,2:end)) >= j && ~ismissing(data{i,j}) && ~isempty(data{i,j})
                curStudentData(end+1) = data{i,j};
            else
                curStudentData(end+1) = curStudentData(end);
            end
        end
    
        curStudentId = data{i,1};
    
    
        %% Put in correct place in the matrix
        underscoreLoc = strfind(curStudentId,'_');
        number = str2num(curStudentId(underscoreLoc(1)+1:underscoreLoc(2)-1));
    
        if contains(curStudent,'Difficulty_Agnostic')
            M_difficulty_agnostic(number+1,:) = M_difficulty_agnostic(number+1,:) + curStudentData;
        elseif contains(curStudent,'Difficulty_Included')
            M_difficulty_included(number+1,:) = M_difficulty_included(number+1,:) + curStudentData;
        else
            M_static(number+1,:) = M_static(number+1,:) + curStudentData;
        end
    
    end
    netsum = netsum + i;
end

%% Sanity Check
fprintf("Net sum of data items is %i.\n",netsum);
fprintf("With %i students, there should be %i concepts.\n",numStudents,netsum/(numStudents*3));
fprintf("We defined %i concepts to be involved.\n",netConcepts);

if netsum/(3*numStudents) == netConcepts
    fprintf("Checks out!\n")
else
    fprintf("Definitions are incorrect.\n")
end

%% Plotting
fig = figure;
hold on;
grid;

p1 = plot(0:(length(curStudentData)-1),sum(M_static)/(netConcepts*numStudents),'k-','LineWidth',5);
b1 = plot(0:(length(curStudentData)-1),sum(M_difficulty_included)/(netConcepts*numStudents),'b-','LineWidth',5);
r1 = plot(0:(length(curStudentData)-1),sum(M_difficulty_agnostic)/(netConcepts*numStudents),'r-','LineWidth',5);

legend([p1,r1,b1],'Average Student Progression for Randomized Questions','Average Student Progression for Hierarchical Bandits (Difficulty Agnostic)','Average Student Progression for Hierarchical Bandits (Difficulty Included)','location','se');

xlabel('Questions Given', 'fontname', 'Times New Roman','FontSize',16,'FontWeight','bold');
ylabel('Mastery Estimation', 'fontname', 'Times New Roman','FontSize',16,'FontWeight','bold');

xlim([0,20]);

set(findall(gcf,'type','text'), 'fontname', 'Times New Roman','FontSize',16);
xticklabel_fs = get(gca,'XTickLabel');
set(gca, 'XTickLabel', xticklabel_fs, 'FontName', 'Times New Roman','FontWeight','normal','FontSize',16);

yticklabel_fs = get(gca,'YTickLabel');
set(gca, 'YTickLabel', yticklabel_fs, 'FontName', 'Times New Roman','FontWeight','normal','FontSize',16);

