--- 
title:  "Where will I await to now?"
date:   2017-05-07 19:58:16 -0600
categories: Task Rx.NET
---

[Link to Code][PureWeen-Repo] 

[Inspiration For Post][ReactiveUI-Issue]
 
A simple example of a Task mixed into a Reactive stream.
 
```csharp

.SelectMany(async alreadyCompletedTask =>
{

    //Here we will be on the UI Thread
    await GetSomeTaskThatMayOrMayNotBeCompleted();
    //Here we will still be on the UI Thread
    //YAY thank you SynchronizationContext
    
    return Unit.Default;
    //Once we leave this block we're not guaranteed to still be on the
    //UI Thread because scheduling may or may not have occurred
})
.Select(_=> //Might be on UI Thread might not be
)
```

The execution frame of the SelectMany before and after the await will reliably stay on the UI Thread. But once reactive has processed the Task and executed the next block you may or may not still be on the UI Thread depending on if Rx needed to schedule a continuation or if it just executed immediately.

If the task has already completed then Reactive uses the [immediate scheduler][Rx.NET-Immediate]

```csharp
private static IObservable<TResult> ToObservableImpl<TResult>(Task<TResult> task, IScheduler scheduler)
{
    var res = default(IObservable<TResult>);

    if (task.IsCompleted)
    {
        scheduler = scheduler ?? ImmediateScheduler.Instance;
    .....
```

Meaning the work will just immediately be scheduled on the current thread.

If the Task still has work to do then the continuation of the stream happens from a ContinueWith which puts us onto a thread from the [thread pool][Rx.NET-ThreadPool].

```csharp
private static IObservable<TResult> ToObservableSlow<TResult>(Task<TResult> task, IScheduler scheduler)
{
    ...
    task.ContinueWith(t => ToObservableDone(task, subject), options);
    ...
}

```

Point being that even if your Task block starts and ends on the UI Thread the following reactive sequences will not for sure be on the UI Thread. You will need to deliberately specify the scheduler if you care about where you will end up. This also applies if you want to ensure that you won't be on the UI Thread.

```csharp

.SelectMany(async alreadyCompletedTask =>
{

    //Here we will be on the UI Thread
    await GetSomeTaskThatMayOrMayNotBeCompleted();
    //Here we will still be on the UI Thread
    //YAY thank you SynchronizationContext
    
    return Unit.Default; 
})
.ObserveOnDispatcher()
.Select(_=> //Now we know we're always on the UI Thread
)
```

This effect threw me off at first because the code after the await is on the UI Thread. As I'm following the path of execution I default to thinking my next sequence after the Task block will just be immediately scheduled. If I haven't explicitly specified a scheduler then it will just execute immediately. This is the thinking that keeps me from writing "ObserveOn" after every single step in an observable sequence. Problem is our async block is going to inconsistently cause scheduling to occur without us really being aware of it and the end result is a block of code that will end up dispatching differently in different cases. 

In the real world I was hit by this with a Xamarin Forms Navigation Page. On Android the Task from the push/pop navigation would complete in such a way that the following Select would continue on the UI Thread whereas on iOS it wouldn't and would just crash horribly. 

It's important to keep in mind the non explicit interactions that can happen when mixing Tasks with IObservables. 

Here's a completish example taken from the [Reproduction WPF App][PureWeen-Repo]
```csharp
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
```

 
An extension I've found helpful as a shorthand way to keep the continuing sequence on the UI Thread

```csharp
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
```



[PureWeen-Repo]: https://github.com/PureWeen/AwaitThenDo
[ReactiveUI-Issue]:   https://github.com/reactiveui/ReactiveUI/pull/1281
[StephenCleary-ContinueWith]:   http://blog.stephencleary.com/2013/10/continuewith-is-dangerous-too.html
[Rx.NET-SourceLink]:   https://github.com/Reactive-Extensions/Rx.NET/blob/master/Rx.NET/Source/System.Reactive.Linq/Reactive/Threading/Tasks/TaskObservableExtensions.cs#L149
[Rx.NET-Immediate]:https://github.com/Reactive-Extensions/Rx.NET/blob/master/Rx.NET/Source/System.Reactive.Linq/Reactive/Threading/Tasks/TaskObservableExtensions.cs#L155
[Rx.NET-ThreadPool]:https://github.com/Reactive-Extensions/Rx.NET/blob/master/Rx.NET/Source/System.Reactive.Linq/Reactive/Threading/Tasks/TaskObservableExtensions.cs#L187

