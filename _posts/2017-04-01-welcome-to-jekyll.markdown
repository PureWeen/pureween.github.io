---
layout: post
title:  "Where will I await to now?"
date:   2017-04-01 19:58:16 -0600
categories: TPL Task Reactive.NET Rx.NET
---

[Link to Code][PureWeen-Repo] 

[Inspiration For Post][ReactiveUI-Issue]

How did I get dispatched here?
"Some Picture"


Here's a Select block that's awaiting on a Task. Let's assume on entry it is on the UI Thread.
{% highlight csharp  %}
    .SelectMany(async alreadyCompletedTask =>
    {

        //Here we will be on the UI Thread
        await GetSomeTaskThatMayOrMayNotBeCompleted();
        //Here we will still be on the UI Thread
        //YAY thank you SynchronizationContext
        
        return Unit.Default;
        //Once we leave this block we're not guarunteed to still be on the
        //UI Thread
    })
    .Select(_=> //Might be on UI Thread might not be
    )
{% endhighlight %} 

Once execution gets to that next Select block you aren't guarunteed to still be on the UI Thread even though the await puts you back there inside the SelectMany.

This is due to how Reactive schedules the continuing block of work. If the task has already completed then it uses the [immediate scheduler][Rx.NET-Immediate]
{% highlight csharp  %}
private static IObservable<TResult> ToObservableImpl<TResult>(Task<TResult> task, IScheduler scheduler)
{
    var res = default(IObservable<TResult>);

    if (task.IsCompleted)
    {
        scheduler = scheduler ?? ImmediateScheduler.Instance;
.....
{% endhighlight %} 

Otherwise a ContinueWith is used at which point we will end up on a thread from the [thread pool][Rx.NET-ThreadPool]

{% highlight csharp  %}
private static IObservable<TResult> ToObservableSlow<TResult>(Task<TResult> task, IScheduler scheduler)
        {
...
            task.ContinueWith(t => ToObservableDone(task, subject), options);
...
        }
{% endhighlight %} 


This threw me off at first because the code after the await will be on the UI Thread. So as I'm following the path of execution I just default to thinking my next Reactive block will just be immediately scheduled onto the same thread. This is the thinking that keeps me from writing "ObserveOn" after every single transformation.  Couple this with the implicit promise of await keeping me on the right thread and the end result is a block of code that will end up dispatching differently only when I'm showing it to a client :-/

Point being that any time you exit a TPL block it's important to always delegate a scheduler otherwise you may see unpredictable behavior. 

I first saw this unpredictability with Xamarin Forms Navigation Pages. On Android the Task from the push/pop navigation would complete in such a way that the following block would continue on the UI Thread whereas on iOS it just crashed horribly. In this case I'm awaiting an operation that's going to happen on the UI Thread so even more so I'm not really thinking that the continued block will leave the UI Thread



Here's a completish example taken from the [Reproduction WPF App][PureWeen-Repo]
{% highlight csharp  %}

runAsAlreadyCompletedTask
    .Merge(runAsNotCompletedTask)
    .SelectMany(async alreadyCompletedTask =>
    {
        //Here we will be on the dispatcher thread
        await GetSomeTaskThatMayOrMayNotBeCompleted();
        //Here we will still be on the dispatcher thread
        WriteCurrentThread("After Await");
        return Unit.Default;
        //Once we leave this block all bets are off what thread we will be on
    })
    .Select(_ =>
    {
        /*
        * If the Task was already completed when checked by Rx then we will
        * still be on the dispatcher.
        * https://github.com/Reactive-Extensions/Rx.NET/blob/master/Rx.NET/Source/System.Reactive.Linq/Reactive/Threading/Tasks/TaskObservableExtensions.cs#L149
        * 
        * Otherwise you will be at the mercy of ContinueWith 
        * http://blog.stephencleary.com/2013/10/continuewith-is-dangerous-too.html. 
        * 
        * I first came across this with code that worked fine on Android 
        * but crashed iOS due to how the timing on the Task worked on one 
        * platform vs the other. 
        * 
        * This can just be unexpected as you are still on the UI Thread 
        * after the await and there are some conditions that will cause 
        * this block to run on the UI Thread and everything will seem fine. 
        * Typically we think of await semantics as a way to be safe about 
        * staying on the UI Thread without having to worry about how we 
        * schedule the continuation ourselves. 
        */
        WriteCurrentThread("Inside Next Observable Block");
        return Unit.Default;
    })
    .Subscribe();
{% endhighlight %} 

 
An extension I've found helpful as a shorthand way to keep the continuing sequence on the UI Thread

{% highlight csharp  %}
/// <summary>
/// I find this to be useful in cases where I am interfacing with a TPL based
/// library i.e. Xamarin.Forms In Xamarin Forms all the Navigation points 
/// are exposed as Task so I use this to expose them 
/// 
/// NavigationPage.PopAsync().ToObservableCurrentThread() 
/// 
/// So that the continuation will remain on the dispatcher thread
/// </summary>
/// <param name="This"></param>
/// <returns></returns>
public static IObservable<Unit> ToObservableCurrentThread(this Task This)
{
    //initially I'd used a Subject but that caused a deadlock
    //This ensures the task will complete before moving on down the Observable
    AsyncSubject<Unit> returnValue = new AsyncSubject<Unit>();

    Observable.StartAsync(async () =>
    {
        try
        {
            if (!This.IsCompleted)
            {
                await This;
            }

            returnValue.OnNext(Unit.Default);
            returnValue.OnCompleted();
        }
        catch (Exception exc)
        {
            returnValue.OnError(exc);
        }

    });

    return returnValue;
} 

{% endhighlight %} 



[PureWeen-Repo]: https://jekyllrb.com/docs/home
[ReactiveUI-Issue]:   https://github.com/reactiveui/ReactiveUI/pull/1281
[StephenCleary-ContinueWith]:   http://blog.stephencleary.com/2013/10/continuewith-is-dangerous-too.html
[Rx.NET-SourceLink]:   https://github.com/Reactive-Extensions/Rx.NET/blob/master/Rx.NET/Source/System.Reactive.Linq/Reactive/Threading/Tasks/TaskObservableExtensions.cs#L149
[Rx.NET-Immediate]:https://github.com/Reactive-Extensions/Rx.NET/blob/master/Rx.NET/Source/System.Reactive.Linq/Reactive/Threading/Tasks/TaskObservableExtensions.cs#L155
[Rx.NET-ThreadPool]:https://github.com/Reactive-Extensions/Rx.NET/blob/master/Rx.NET/Source/System.Reactive.Linq/Reactive/Threading/Tasks/TaskObservableExtensions.cs#L187

