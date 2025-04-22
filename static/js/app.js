$(function(){
    $.getJSON('/data', function(data){
      window.appData = data;
      var page = $('body').attr('id');
      if(page === 'learn-page') initLearn();
      if(page === 'quiz-page')  initQuiz();
    });
  });
  
  function initLearn(){
    var id = +$('body').data('lesson-id');
    var lesson = appData.lessons.find(l=>l.id===id);
    $('.lesson-title').text(lesson.title);
    $('.lesson-details').empty();
    lesson.details.forEach(d=>$('.lesson-details')
      .append('<li class="list-group-item">'+d+'</li>'));
    if($('#prev-btn').length)
      $('#prev-btn').click(()=>location='/learn/'+(id-1));
    if($('#next-btn').length)
      $('#next-btn').click(()=>location='/learn/'+(id+1));
    if($('#to-quiz-btn').length)
      $('#to-quiz-btn').click(()=>location='/quiz/1');
  }
  
  function initQuiz(){
    var id = +$('body').data('quiz-id');
    var q = appData.quiz.find(x=>x.id===id);
    $('.quiz-question').text(q.question);
  }